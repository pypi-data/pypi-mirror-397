"""
SPConv preprocessing: Dense fused images with RGB + LiDAR features from intermediate labeled files.
Output:
  - fused_images: (13, H, W) - 3 RGB + 10 LiDAR features [x,y,z,intensity,reflectivity,ring,ambient,range,u_norm,v_norm]
  - masks: (10, H, W) - Spatial validity mask for LiDAR channels
  Only ground points (is_ground=True) are projected. Multiple points averaged per pixel.

Reads from intermediate H5 files (output of preprocess_labels.py) which contain:
- Pre-computed Magic Formula D labels
- Geospatially filtered patches (only patches where measurement wheel drove over)
- Bounding boxes and image indices for each valid patch
"""
import numpy as np
import torch
import h5py
from typing import Dict, Optional, Tuple, List
import logging

from .preprocess_base import IntermediatePreprocessor, IntermediatePreprocessConfig, LazyLidarTable
from .normalizers import OusterLidarNormalizer, RGBNormalizer


logger = logging.getLogger(__name__)

# Native patch size from H5 files (all patches are this exact size)
PATCH_SIZE = (223, 223)


class SPConvPreprocessor(IntermediatePreprocessor):
    """Preprocessor for SPConv: Images + 2D sparse points from intermediate labeled files."""

    def __init__(self, config: IntermediatePreprocessConfig):
        self._lidar_table = None
        super().__init__(config)

    def _initialize_tools(self) -> Dict:
        """Initialize normalizers."""
        logger.info(f"Using device: {self.device}")
        logger.info(f"Patch size: {PATCH_SIZE}")

        return {
            'lidar_normalizer': OusterLidarNormalizer(
                sensor_model=self.config.sensor_model,
                max_range=self.config.max_lidar_range
            ),
            'rgb_normalizer': RGBNormalizer()
        }

    def _get_output_datasets_spec(self) -> Dict[str, Dict]:
        """Specify output datasets."""
        H, W = PATCH_SIZE
        return {
            'fused_images': {
                'shape': (13, H, W),  # 3 RGB + 10 LiDAR
                'dtype': 'f4'
            },
            'masks': {
                'shape': (10, H, W),  # Spatial validity mask
                'dtype': 'bool'
            },
            'labels': {
                'shape': (),
                'dtype': 'f4'
            },
            'original_indices': {
                'shape': (),
                'dtype': 'i4'
            }
        }

    def _process_file(self, intermediate_file, source_file, dest_file):
        """Override to initialize LiDAR table before processing."""
        self._current_source_file = source_file.name
        self._current_dest_file = dest_file

        # Load intermediate data
        with h5py.File(intermediate_file, 'r') as f_int:
            patch_indices = f_int['patch_indices'][:]
            labels = f_int['labels'][:]
            bboxes = f_int['bounding_boxes'][:]
            image_indices = f_int['image_indices'][:]
            mf_d_param = f_int.attrs.get('mf_d_parameter', 0.0)

            logger.info(f"Loaded {len(patch_indices)} labeled patches from intermediate file")
            logger.info(f"MF D parameter: {mf_d_param:.3f}")

        # Process patches using source file for raw data
        with h5py.File(source_file, 'r') as f_src:
            # Initialize LiDAR table for this file
            self._lidar_table = LazyLidarTable(
                f_src,
                self.config.lidar_table_key,
                self.config.lidar_frame_idx_key
            )

            processed, skipped = self._process_all_patches(
                f_src, patch_indices, labels, bboxes, image_indices
            )

        return processed, skipped

    def _process_single_patch(
        self,
        patch_idx: int,
        image_idx: int,
        label: float,
        bbox: np.ndarray,
        f_src,
        rgb_image: torch.Tensor
    ) -> Optional[Dict[str, np.ndarray]]:
        """Process single patch for SPConv with dense fusion."""
        try:
            # Convert bbox array to dict
            bbox_dict = {
                'top_left_u': int(bbox[0]),
                'top_left_v': int(bbox[1]),
                'bottom_right_u': int(bbox[2]),
                'bottom_right_v': int(bbox[3])
            }

            # Extract and resize image patch
            image_patch = self._extract_image_patch(rgb_image, bbox_dict)

            # Get lidar data
            lidar_pts = self._prepare_lidar_data(image_idx, bbox_dict)

            if lidar_pts.shape[0] == 0:
                return None

            # Create dense LiDAR features with averaging
            lidar_features, spatial_mask = self._create_dense_lidar_features(
                lidar_pts, bbox_dict
            )

            # Normalize LiDAR features (first 8 channels: x, y, z, intensity, reflectivity, ring, ambient, range)
            # Channels 8-9 (u_norm, v_norm) are already in [0,1]
            H, W = lidar_features.shape[1], lidar_features.shape[2]
            lidar_8ch = lidar_features[:8].reshape(8, -1).T  # (H*W, 8)
            lidar_8ch_norm = self.tools['lidar_normalizer'].normalize(lidar_8ch)
            lidar_features[:8] = lidar_8ch_norm.T.reshape(8, H, W)

            # Normalize image
            image_patch = self.tools['rgb_normalizer'].normalize(image_patch)

            # Mask RGB to black where no ground points (using first channel of spatial_mask)
            no_ground_mask = ~spatial_mask[0]  # Inverse of valid pixels
            image_patch[:, no_ground_mask] = 0.0  # Set RGB to black (0,0,0)

            # Concatenate RGB (3, H, W) + LiDAR (10, H, W) -> fused (13, H, W)
            fused_image = np.concatenate([image_patch, lidar_features], axis=0)

            return {
                'fused_images': fused_image,
                'masks': spatial_mask,
                'labels': label,
                'original_indices': patch_idx
            }
        except Exception as e:
            logger.debug(f"Patch {patch_idx} error: {e}")
            return None

    def _extract_image_patch(self, rgb_image: torch.Tensor, bbox: dict) -> np.ndarray:
        """Extract image patch (native 223x223 size, no resize needed).

        Args:
            rgb_image: Image in HWC format (from base class permute)
            bbox: Bounding box dict with top_left_v, bottom_right_v, top_left_u, bottom_right_u

        Returns:
            Patch in CHW format (3, H, W)
        """
        # rgb_image is HWC format, slice accordingly
        patch_hwc = rgb_image[
            bbox['top_left_v']:bbox['bottom_right_v'],  # H (rows)
            bbox['top_left_u']:bbox['bottom_right_u'],  # W (cols)
            :  # C (channels)
        ]
        # Convert to CHW format
        patch_chw = patch_hwc.permute(2, 0, 1)
        return patch_chw.cpu().numpy().astype(np.float32)

    def _prepare_lidar_data(self, image_idx: int, bbox: dict) -> np.ndarray:
        """Prepare lidar data with is_ground field (12 columns total)."""
        frame_lidar_data = self._lidar_table.get_frame(image_idx)

        if frame_lidar_data.shape[0] == 0:
            return np.zeros((0, 12), dtype=np.float32)

        bbox_u_min = bbox['top_left_u']
        bbox_v_min = bbox['top_left_v']
        bbox_u_max = bbox['bottom_right_u']
        bbox_v_max = bbox['bottom_right_v']

        point_u = frame_lidar_data['u']
        point_v = frame_lidar_data['v']

        mask = (
            (point_u >= bbox_u_min) & (point_u <= bbox_u_max) &
            (point_v >= bbox_v_min) & (point_v <= bbox_v_max)
        )

        filtered_data = frame_lidar_data[mask]
        n_points = filtered_data.shape[0]

        if n_points == 0:
            return np.zeros((0, 12), dtype=np.float32)

        lidar_pts = np.zeros((n_points, 12), dtype=np.float32)
        lidar_pts[:, 0] = filtered_data['x']
        lidar_pts[:, 1] = filtered_data['y']
        lidar_pts[:, 2] = filtered_data['z']
        lidar_pts[:, 3] = filtered_data['intensity']
        lidar_pts[:, 4] = filtered_data['reflectivity']
        lidar_pts[:, 5] = filtered_data['ring']
        lidar_pts[:, 6] = filtered_data['ambient']
        lidar_pts[:, 7] = filtered_data['range']
        lidar_pts[:, 8] = filtered_data['u']
        lidar_pts[:, 9] = filtered_data['v']
        # Check if is_ground field exists in structured array
        if 'is_ground' in filtered_data.dtype.names:
            lidar_pts[:, 10] = filtered_data['is_ground']
        else:
            lidar_pts[:, 10] = np.ones(n_points)  # Default to ground if not available
        lidar_pts[:, 11] = 0  # Reserved for future use

        return lidar_pts

    def _create_dense_lidar_features(
        self,
        lidar_pts: np.ndarray,
        bbox: dict
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Create dense LiDAR feature representation with averaging.

        Returns:
            lidar_features: (10, H, W) - Dense LiDAR features
            spatial_mask: (10, H, W) - Boolean mask for valid pixels
        """
        H = bbox['bottom_right_v'] - bbox['top_left_v']
        W = bbox['bottom_right_u'] - bbox['top_left_u']

        # Initialize dense arrays
        lidar_features = np.zeros((10, H, W), dtype=np.float32)
        spatial_mask = np.zeros((10, H, W), dtype=bool)

        if lidar_pts.shape[0] == 0:
            return lidar_features, spatial_mask

        # Filter ground points ONLY (is_ground == 1)
        is_ground = lidar_pts[:, 10]
        ground_mask = is_ground == 1
        ground_pts = lidar_pts[ground_mask]

        if ground_pts.shape[0] == 0:
            return lidar_features, spatial_mask

        # Get UV coordinates
        u_full = ground_pts[:, 8]
        v_full = ground_pts[:, 9]

        # Filter by patch bounds
        in_patch = (
            (u_full >= bbox['top_left_u']) &
            (u_full < bbox['bottom_right_u']) &
            (v_full >= bbox['top_left_v']) &
            (v_full < bbox['bottom_right_v'])
        )

        patch_pts = ground_pts[in_patch]

        if patch_pts.shape[0] == 0:
            return lidar_features, spatial_mask

        u_in_patch = u_full[in_patch]
        v_in_patch = v_full[in_patch]

        u_patch = u_in_patch - bbox['top_left_u']
        v_patch = v_in_patch - bbox['top_left_v']

        # Normalize UV to [0, 1]
        u_norm = u_patch / W
        v_norm = v_patch / H

        # Round to integer pixel locations
        u_idx = np.clip(np.round(u_patch).astype(np.int32), 0, W - 1)
        v_idx = np.clip(np.round(v_patch).astype(np.int32), 0, H - 1)

        # Extract features: [x, y, z, intensity, reflectivity, ring, ambient, range, u_norm, v_norm]
        features_per_point = np.column_stack([
            patch_pts[:, 0],  # x
            patch_pts[:, 1],  # y
            patch_pts[:, 2],  # z
            patch_pts[:, 3],  # intensity
            patch_pts[:, 4],  # reflectivity
            patch_pts[:, 5],  # ring
            patch_pts[:, 6],  # ambient
            patch_pts[:, 7],  # range
            u_norm,           # u_normalized
            v_norm,           # v_normalized
        ])  # Shape: (N, 10)

        # Accumulate features using efficient binning
        feature_sums = np.zeros((H, W, 10), dtype=np.float64)
        counts = np.zeros((H, W), dtype=np.int32)

        # Accumulate features at each pixel location
        for i in range(patch_pts.shape[0]):
            v, u = v_idx[i], u_idx[i]
            feature_sums[v, u] += features_per_point[i]
            counts[v, u] += 1

        # Average where points exist
        valid_pixels = counts > 0
        for c in range(10):
            lidar_features[c][valid_pixels] = (
                feature_sums[:, :, c][valid_pixels] / counts[valid_pixels]
            )
            spatial_mask[c] = valid_pixels

        return lidar_features, spatial_mask

    def _write_batch_results(
        self,
        f_dst,
        datasets: Dict,
        batch_results: List[Optional[Dict]],
        valid_count: int
    ) -> Tuple[int, int]:
        """Write batch results to output file (fixed-size images)."""
        batch_fused = []
        batch_masks = []
        batch_labels = []
        batch_original_indices = []
        skipped_count = 0

        for result in batch_results:
            if result is not None:
                batch_fused.append(result['fused_images'])
                batch_masks.append(result['masks'])
                batch_labels.append(result['labels'])
                batch_original_indices.append(result['original_indices'])
            else:
                skipped_count += 1

        if batch_fused:
            n_valid = len(batch_fused)
            new_count = valid_count + n_valid

            # Resize and write all datasets
            for name in ['fused_images', 'masks', 'labels', 'original_indices']:
                datasets[name].resize(new_count, axis=0)

            datasets['fused_images'][valid_count:new_count] = batch_fused
            datasets['masks'][valid_count:new_count] = batch_masks
            datasets['labels'][valid_count:new_count] = batch_labels
            datasets['original_indices'][valid_count:new_count] = batch_original_indices

            f_dst.flush()
            return n_valid, skipped_count

        return 0, skipped_count


def preprocess_spconv(config: Optional[IntermediatePreprocessConfig] = None):
    """Main entry point for SPConv preprocessing from intermediate files."""
    if config is None:
        config = IntermediatePreprocessConfig(
            intermediate_folder="/home/uggld/Desktop/trfc_estimation_camera/data/intermediate/labeled",
            source_folder="/mnt/Workspace_encrypted/new_rosbags/2025-12-03/synchronized",
            dest_folder="/home/uggld/Desktop/trfc_estimation_camera/data/preprocessed/SpConv",
            lidar_table_key='hi5/road/lidar_point_cloud/data/all_points',
            lidar_frame_idx_key='hi5/road/lidar_point_cloud/data/frame_start_indices'
        )

    preprocessor = SPConvPreprocessor(config)
    preprocessor.run()


if __name__ == "__main__":
    preprocess_spconv()
