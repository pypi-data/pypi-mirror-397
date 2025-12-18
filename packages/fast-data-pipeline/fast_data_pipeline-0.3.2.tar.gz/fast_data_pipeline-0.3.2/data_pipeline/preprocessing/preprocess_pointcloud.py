"""
PointNet preprocessing: Using pre-computed UV coordinates from intermediate labeled files.
Output: (N, 13) - [x,y,z, 5 lidar features, u_norm, v_norm, R,G,B]

Reads from intermediate H5 files (output of preprocess_labels.py) which contain:
- Pre-computed Magic Formula D labels
- Geospatially filtered patches (only patches where measurement wheel drove over)
- Bounding boxes and image indices for each valid patch
"""
import numpy as np
import torch
import h5py
from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass
import logging

from .preprocess_base import IntermediatePreprocessor, IntermediatePreprocessConfig, LazyLidarTable
from .normalizers import OusterLidarNormalizer, RGBNormalizer


logger = logging.getLogger(__name__)


@dataclass
class FeatureIndices:
    """Indices for feature array columns."""
    X: int = 0
    Y: int = 1
    Z: int = 2
    INTENSITY: int = 3
    REFLECTIVITY: int = 4
    RING: int = 5
    AMBIENT: int = 6
    RANGE: int = 7
    U: int = 8
    V: int = 9
    IS_GROUND: int = 10

    LIDAR_END: int = 8
    RGB_START: int = 8
    RGB_END: int = 11


class PointNetPreprocessor(IntermediatePreprocessor):
    """Preprocessor for PointNet using pre-labeled intermediate files."""

    BASE_LIDAR_DIM = 8
    UV_DIM = 2
    RGB_DIM = 3
    OUTPUT_DIM = 13  # 8 lidar + 2 UV + 3 RGB

    def __init__(self, config: IntermediatePreprocessConfig):
        self.feat = FeatureIndices()
        self._lidar_table = None
        super().__init__(config)

    def _initialize_tools(self) -> Dict:
        """Initialize normalizers."""
        logger.info(f"Using device: {self.device}")
        logger.info(f"Using pre-computed UV coordinates")
        logger.info(f"Output dimension: {self.OUTPUT_DIM}")

        return {
            'lidar_normalizer': OusterLidarNormalizer(
                sensor_model=self.config.sensor_model,
                max_range=self.config.max_lidar_range
            ),
            'rgb_normalizer': RGBNormalizer()
        }

    def _get_output_datasets_spec(self) -> Dict[str, Dict]:
        """Specify output datasets for variable-length storage."""
        return {
            'points': {
                'shape': (self.OUTPUT_DIM,),
                'dtype': 'f4',
                'is_variable': True
            },
            'point_start_indices': {
                'shape': (),
                'dtype': 'i8'
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
        """Process single patch for PointNet (feature extraction only)."""
        try:
            # Convert bbox array to dict
            bbox_dict = {
                'top_left_u': int(bbox[0]),
                'top_left_v': int(bbox[1]),
                'bottom_right_u': int(bbox[2]),
                'bottom_right_v': int(bbox[3])
            }

            # Get LiDAR data
            lidar_pts_with_uv = self._prepare_lidar_data(image_idx)

            if lidar_pts_with_uv is None or lidar_pts_with_uv.shape[0] == 0:
                return None

            # Process point features
            processed_points = self._process_point_features(
                lidar_pts_with_uv,
                rgb_image,
                bbox_dict
            )

            if processed_points.shape[0] == 0:
                return None

            return {
                'points': processed_points,
                'labels': label,
                'original_indices': patch_idx
            }
        except Exception as e:
            logger.debug(f"Patch {patch_idx} error: {e}")
            return None

    def _prepare_lidar_data(self, image_idx: int) -> np.ndarray:
        """Extract lidar features with UV and ground flag."""
        frame_data = self._lidar_table.get_frame(image_idx)

        if frame_data.shape[0] == 0:
            return np.zeros((0, 11), dtype=np.float32)

        feature_keys = [
            'x', 'y', 'z', 'intensity', 'reflectivity',
            'ring', 'ambient', 'range', 'u', 'v', 'is_ground'
        ]

        return np.column_stack(
            [frame_data[key] for key in feature_keys]
        ).astype(np.float32)

    def _filter_points_by_patch(
        self,
        lidar_pts_with_uv: np.ndarray,
        bbox: Dict[str, int]
    ) -> np.ndarray:
        """Filter points within patch boundaries."""
        if lidar_pts_with_uv.shape[0] == 0:
            return np.zeros((0, 11), dtype=np.float32)

        u = lidar_pts_with_uv[:, self.feat.U]
        v = lidar_pts_with_uv[:, self.feat.V]
        is_ground = lidar_pts_with_uv[:, self.feat.IS_GROUND]

        in_patch = (
            (u >= bbox['top_left_u']) &
            (u < bbox['bottom_right_u']) &
            (v >= bbox['top_left_v']) &
            (v < bbox['bottom_right_v']) &
            (is_ground > 0)
        )

        return lidar_pts_with_uv[in_patch]

    def _sample_rgb_at_uv(
        self,
        points: np.ndarray,
        rgb_image_hwc: torch.Tensor
    ) -> np.ndarray:
        """Sample RGB values at UV coordinates (GPU accelerated)."""
        u_int = torch.from_numpy(points[:, self.feat.U].astype(np.int64)).to(self.device)
        v_int = torch.from_numpy(points[:, self.feat.V].astype(np.int64)).to(self.device)

        u_int = torch.clamp(u_int, 0, rgb_image_hwc.shape[1] - 1)
        v_int = torch.clamp(v_int, 0, rgb_image_hwc.shape[0] - 1)

        rgb_values = rgb_image_hwc[v_int, u_int, :]

        return rgb_values.cpu().numpy()

    def _normalize_features(
        self,
        lidar_features: np.ndarray,
        rgb_values: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Normalize lidar and RGB features."""
        normalized_lidar = self.tools['lidar_normalizer'].normalize(lidar_features)
        normalized_rgb = self.tools['rgb_normalizer'].normalize(rgb_values)

        return normalized_lidar, normalized_rgb

    def _build_feature_vector(
        self,
        lidar_features: np.ndarray,
        uv_norm: np.ndarray,
        rgb_values: np.ndarray
    ) -> np.ndarray:
        """Concatenate lidar, UV, and RGB features."""
        return np.concatenate(
            [lidar_features, uv_norm, rgb_values],
            axis=1
        ).astype(np.float32)

    def _process_point_features(
        self,
        lidar_pts_with_uv: np.ndarray,
        rgb_image_hwc: torch.Tensor,
        bbox: Dict[str, int]
    ) -> np.ndarray:
        """Filter, sample RGB, normalize features, and compute normalized UV."""
        filtered_points = self._filter_points_by_patch(lidar_pts_with_uv, bbox)

        if filtered_points.shape[0] == 0:
            return np.zeros((0, self.OUTPUT_DIM), dtype=np.float32)

        # Extract UV coordinates and calculate patch-relative normalized values
        u_full = filtered_points[:, self.feat.U]
        v_full = filtered_points[:, self.feat.V]

        # Patch-relative coordinates
        u_patch = u_full - bbox['top_left_u']
        v_patch = v_full - bbox['top_left_v']

        # Patch dimensions
        patch_width = bbox['bottom_right_u'] - bbox['top_left_u']
        patch_height = bbox['bottom_right_v'] - bbox['top_left_v']

        # Normalize to [0, 1] range
        u_norm = (u_patch / patch_width).reshape(-1, 1)
        v_norm = (v_patch / patch_height).reshape(-1, 1)
        uv_norm = np.concatenate([u_norm, v_norm], axis=1).astype(np.float32)

        # Extract lidar features (without UV)
        lidar_features = filtered_points[:, :self.feat.LIDAR_END]
        rgb_values = self._sample_rgb_at_uv(filtered_points, rgb_image_hwc)

        normalized_lidar, normalized_rgb = self._normalize_features(
            lidar_features,
            rgb_values
        )

        return self._build_feature_vector(normalized_lidar, uv_norm, normalized_rgb)

    def _write_batch_results(
        self,
        f_dst,
        datasets: Dict,
        batch_results: List[Optional[Dict]],
        valid_count: int
    ) -> Tuple[int, int]:
        """Write batch results to output file (variable-length points)."""
        batch_points = []
        batch_start_indices = []
        batch_labels = []
        batch_original_indices = []
        skipped_count = 0

        # Get current total points
        total_points = datasets['points'].shape[0]

        for result in batch_results:
            if result is not None:
                points = result['points']
                batch_start_indices.append(total_points)
                batch_points.append(points)
                batch_labels.append(result['labels'])
                batch_original_indices.append(result['original_indices'])
                total_points += len(points)
            else:
                skipped_count += 1

        if batch_points:
            n_valid = len(batch_points)

            # Concatenate all points
            all_batch_points = np.concatenate(batch_points, axis=0)

            # Resize and write points
            current_points = datasets['points'].shape[0]
            datasets['points'].resize(current_points + len(all_batch_points), axis=0)
            datasets['points'][current_points:] = all_batch_points

            # Resize and write per-patch data
            new_patch_count = valid_count + n_valid
            datasets['point_start_indices'].resize(new_patch_count, axis=0)
            datasets['point_start_indices'][valid_count:new_patch_count] = batch_start_indices

            datasets['labels'].resize(new_patch_count, axis=0)
            datasets['labels'][valid_count:new_patch_count] = batch_labels

            datasets['original_indices'].resize(new_patch_count, axis=0)
            datasets['original_indices'][valid_count:new_patch_count] = batch_original_indices

            f_dst.flush()
            return n_valid, skipped_count

        return 0, skipped_count


def preprocess_pointnet(config: Optional[IntermediatePreprocessConfig] = None):
    """Main entry point for PointNet preprocessing from intermediate files."""
    if config is None:
        config = IntermediatePreprocessConfig(
            intermediate_folder="/home/uggld/Desktop/trfc_estimation_camera/data/intermediate/labeled",
            source_folder="/mnt/Workspace_encrypted/new_rosbags/2025-12-03/synchronized",
            dest_folder="/home/uggld/Desktop/trfc_estimation_camera/data/preprocessed/PointNet++",
            lidar_table_key='hi5/road/lidar_point_cloud/data/all_points',
            lidar_frame_idx_key='hi5/road/lidar_point_cloud/data/frame_start_indices'
        )

    preprocessor = PointNetPreprocessor(config)
    preprocessor.run()


if __name__ == "__main__":
    preprocess_pointnet()
