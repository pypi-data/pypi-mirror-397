"""
Base preprocessing pipeline with integrated progress monitoring.
"""
import h5py
import numpy as np
import torch
from scipy.spatial import cKDTree
from collections import OrderedDict
from pathlib import Path
from typing import Tuple, Optional, Dict, List, Any
from dataclasses import dataclass
from abc import ABC, abstractmethod
import logging
import glob
from tqdm import tqdm
from data_pipeline.preprocessing.h5_utils import validate_h5_preprocessing_structure, safe_h5_index
from data_pipeline.preprocessing.normalizers import OusterLidarNormalizer, RGBNormalizer
from data_pipeline.preprocessing.label_extractors import MagicFormulaGeoExtractor, MagicFormulaGeoConfig
from kornia.color import raw_to_rgb, CFA


logger = logging.getLogger(__name__)


@dataclass
class PreprocessConfig:
    """Base configuration for preprocessing."""
    source_folder: str
    dest_folder: str
    source_pattern: str = "*.h5"
    output_suffix: str = "_preprocessed"
    skip_existing: bool = True
    
    min_points: int = 100
    image_full_size: Tuple[int, int] = (3032, 5032)
    
    patch_table_key: str = 'hi5/road/road_patches/pointcloud_data'
    patch_num_key: str = 'hi5/road/road_patches/num_patches'
    
    patch_ts_s_key: str = 'hi5/road/road_patches/timestamp/timestamp_s'
    patch_ts_ns_key: str = 'hi5/road/road_patches/timestamp/timestamp_ns'
    
    cam_ts_s_key: str = 'hi5/road/image/timestamp/timestamp_s'
    cam_ts_ns_key: str = 'hi5/road/image/timestamp/timestamp_ns'
    cam_img_key: str = 'hi5/road/image/data'
    
    lidar_table_key: str = 'hi5/road/lidar_point_cloud/data/all_points'
    lidar_frame_idx_key: str = 'hi5/road/lidar_point_cloud/data/frame_start_indices'
    lidar_ts_s_key: str = 'hi5/road/lidar_point_cloud/timestamp/timestamp_s'
    lidar_ts_ns_key: str = 'hi5/road/lidar_point_cloud/timestamp/timestamp_ns'
    
    # Labels
    label_key: str = "rfmu/marwis/data/friction"
    label_type: str = "marwis"  # "marwis" or "magic_formula"
    label_key_mf: str = "rfmu/magic_formula/D"  # Key for precomputed MF D parameter

    # Brake data validation (for Magic Formula label extraction)
    validate_brake_data: bool = True  # Enabled by default
    brake_position_key: str = "rfmu/vehicle_data/brake_actuator_position_mm"
    brake_threshold_mm: float = 1.0  # Match MagicFormulaGeoConfig default
    min_brake_samples: int = 100  # Minimum absolute count (balanced threshold)
    min_brake_percentage: float = 2.0  # Minimum percentage (lenient threshold)

    # Model config
    sensor_model: str = "OS-2"
    max_lidar_range: float = 240.0
    
    # Processing config
    batch_size: int = 32
    max_cache_size: int = 20


class LazyLidarTable:
    """Lazy loader for lidar data."""
    
    def __init__(self, h5_file, table_key: str, frame_idx_key: str):
        self.h5_file = h5_file
        self.table_key = table_key
        self.frame_indices = h5_file[frame_idx_key][:]
    
    def get_frame(self, image_idx: int) -> np.ndarray:
        """Load frame for given image index."""
        point_start = int(self.frame_indices[image_idx])
        
        if image_idx + 1 >= len(self.frame_indices):
            point_end = len(self.h5_file[self.table_key])
        else:
            point_end = int(self.frame_indices[image_idx + 1])
        
        if point_end <= point_start:
            return np.zeros((0, 11), dtype=np.float32)
        
        return self.h5_file[self.table_key][point_start:point_end]


class BasePreprocessor(ABC):
    """Base class for preprocessing pipelines with integrated progress bars."""
    
    def __init__(self, config: PreprocessConfig):
        self.config = config
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        self.image_cache = OrderedDict()
        self.tools = self._initialize_tools()
        
        # Progress tracking
        self.pbar_files = None
        self.pbar_patches = None

    @staticmethod
    def combine_timestamps(ts_s: np.ndarray, ts_ns: np.ndarray) -> np.ndarray:
        """Combine seconds and nanoseconds into precise timestamp.
        
        Args:
            ts_s: Timestamps in seconds
            ts_ns: Timestamps in nanoseconds
            
        Returns:
            Combined timestamps as float64 seconds
        """
        return ts_s.astype(np.float64) + ts_ns.astype(np.float64) * 1e-9
    
    @abstractmethod
    def _initialize_tools(self) -> Dict:
        """Initialize tools (projector, normalizers, etc.)."""
        pass
    
    @abstractmethod
    def _get_output_datasets_spec(self) -> Dict[str, Dict]:
        """Specify output dataset structure."""
        pass
    
    @abstractmethod
    def _process_single_patch(
        self,
        patch_idx: int,
        image_idx: int,
        f_src,
        metadata,
        rgb_image: torch.Tensor
    ) -> Optional[Dict[str, np.ndarray]]:
        """Process single patch."""
        pass
    
    def run(self):
        """Execute preprocessing for all files with progress bars."""
        print("\n" + "="*80)
        print("PREPROCESSING STARTED")
        print("="*80)
        
        source_path = Path(self.config.source_folder)
        dest_path = Path(self.config.dest_folder)
        dest_path.mkdir(parents=True, exist_ok=True)
        
        print(f"Source: {source_path}")
        print(f"Dest:   {dest_path}")
        print(f"Device: {self.device}")
        
        h5_files = self._discover_files(source_path)
        
        if not h5_files:
            logger.warning(f"No files matching '{self.config.source_pattern}' found")
            return
        
        print(f"\nFound {len(h5_files)} files to process:")
        for i, f in enumerate(h5_files, 1):
            size_mb = f.stat().st_size / (1024 * 1024)
            print(f"  {i}. {f.name} ({size_mb:.1f} MB)")
        print("="*80 + "\n")
        
        # File-level progress bar
        self.pbar_files = tqdm(
            total=len(h5_files),
            desc="Files",
            unit="file",
            position=0,
            leave=True,
            bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]'
        )
        
        successful = 0
        failed = 0
        
        for idx, source_file in enumerate(h5_files):
            dest_file = self._get_output_path(source_file, dest_path)
            
            # Update file progress description
            self.pbar_files.set_description(f"Files [{source_file.name}]")
            
            if self.config.skip_existing and dest_file.exists():
                self.pbar_files.write(f"⊘ Skipping {source_file.name} (already exists)")
                self.pbar_files.update(1)
                successful += 1
                continue
            
            try:
                processed, skipped = self._process_file(source_file, dest_file)
                self.pbar_files.write(
                    f"✓ {source_file.name}: {processed} processed, {skipped} skipped"
                )
                successful += 1
            except Exception as e:
                self.pbar_files.write(f"✗ {source_file.name}: {str(e)}")
                logger.exception(e)
                failed += 1
                
                if dest_file.exists():
                    dest_file.unlink()
            
            # Update file progress
            self.pbar_files.update(1)
            
            # Cleanup
            self.image_cache.clear()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        
        # Close file progress bar
        self.pbar_files.close()
        
        # Final summary
        print("\n" + "="*80)
        print("PREPROCESSING COMPLETE")
        print(f"  Total:      {len(h5_files)}")
        print(f"  Successful: {successful}")
        print(f"  Failed:     {failed}")
        print("="*80 + "\n")
    
    def _discover_files(self, source_path: Path) -> List[Path]:
        """Discover H5 files."""
        pattern = str(source_path / self.config.source_pattern)
        files = [Path(f) for f in glob.glob(pattern)]
        files = [f for f in files if self.config.output_suffix not in f.stem]
        return sorted(files)
    
    def _get_output_path(self, source_file: Path, dest_folder: Path) -> Path:
        """Generate output path."""
        output_name = f"{source_file.stem}{self.config.output_suffix}.h5"
        return dest_folder / output_name
    
    def _process_file(self, source_file: Path, dest_file: Path) -> Tuple[int, int]:
        """Process single file with validation and streaming writes."""
        self._current_source_file = source_file.name
        self._current_dest_file = dest_file
        
        # Validate file structure first
        with h5py.File(source_file, 'r') as f_src:
            # Check required keys exist
            required_keys = {
                'patch_table': self.config.patch_table_key,
                'patch_ts_s': self.config.patch_ts_s_key,
                'patch_ts_ns': self.config.patch_ts_ns_key,
                'cam_ts_s': self.config.cam_ts_s_key,
                'cam_ts_ns': self.config.cam_ts_ns_key,
                'cam_img': self.config.cam_img_key,
                'lidar_table': self.config.lidar_table_key,
                'lidar_idx': self.config.lidar_frame_idx_key,
                'lidar_ts_s': self.config.lidar_ts_s_key,
                'lidar_ts_ns': self.config.lidar_ts_ns_key
            }
            
            
            
            is_valid, missing = validate_h5_preprocessing_structure(f_src, required_keys)
            
            if not is_valid:
                raise ValueError(
                    f"Invalid file structure. Missing keys:\n  " +
                    "\n  ".join(missing)
                )

            # Validate brake data BEFORE processing patches
            self._validate_brake_data(f_src)

            # Load metadata
            metadata = self._load_metadata(f_src)
            if metadata is None:
                raise ValueError("Failed to load metadata")
            
            # Check if file has any patches
            if metadata['num_patches'] == 0:
                raise ValueError("File contains 0 patches")
            
            # Process patches
            valid_indices, processed, skipped = self._process_all_patches(f_src, metadata)
        
        return processed, skipped
    
    def _load_metadata(self, h5_file) -> Optional[Dict]:
        """Load metadata with precise timestamp synchronization."""
        try:
            # Combine patch timestamps
            patch_ts_s = h5_file[self.config.patch_ts_s_key][:]
            patch_ts_ns = h5_file[self.config.patch_ts_ns_key][:]
            patch_timestamps = self.combine_timestamps(patch_ts_s, patch_ts_ns)
            
            # Combine camera timestamps
            cam_ts_s = h5_file[self.config.cam_ts_s_key][:]
            cam_ts_ns = h5_file[self.config.cam_ts_ns_key][:]
            cam_timestamps = self.combine_timestamps(cam_ts_s, cam_ts_ns)
            
            # Combine lidar timestamps
            lidar_ts_s = h5_file[self.config.lidar_ts_s_key][:]
            lidar_ts_ns = h5_file[self.config.lidar_ts_ns_key][:]
            lidar_timestamps = self.combine_timestamps(lidar_ts_s, lidar_ts_ns)
            
            # Get patch data
            patch_table = h5_file[self.config.patch_table_key]
            num_patches_total = patch_table.shape[0]
            
            # Load per-frame patch counts
            num_patches_per_frame = h5_file['hi5/road/road_patches/num_patches'][:]
            
            logger.info(
                f"Per-frame patches: {len(num_patches_per_frame)} frames, "
                f"avg {num_patches_per_frame.mean():.1f} patches/frame, "
                f"total {num_patches_per_frame.sum()} patches"
            )

            # Fixed: Include all frames in cumsum (removed [:-1])
            # This creates N+1 indices for N frames: [0, cumsum[0], cumsum[1], ..., total]
            patch_start_indices = np.concatenate([[0], np.cumsum(num_patches_per_frame)])

            # Build patch->frame mapping
            patch_to_frame = np.zeros(num_patches_total, dtype=int)
            for frame_idx in range(len(num_patches_per_frame)):
                start_idx = patch_start_indices[frame_idx]
                end_idx = patch_start_indices[frame_idx + 1]  # Safe now: array has N+1 elements
                patch_to_frame[start_idx:end_idx] = frame_idx
            
            # Build KDTree for camera timestamp lookup
            kdtree = cKDTree(cam_timestamps.reshape(-1, 1))
            
            metadata = {
                'num_patches': num_patches_total,
                'patch_table': patch_table,
                'patch_timestamps': patch_timestamps,
                'cam_timestamps': cam_timestamps,
                'lidar_timestamps': lidar_timestamps,
                'lidar_table': LazyLidarTable(
                    h5_file,
                    self.config.lidar_table_key,
                    self.config.lidar_frame_idx_key
                ),
                'kdtree': kdtree,
                'patch_to_list': patch_to_frame,
                'patch_list_ts': patch_timestamps
            }
            
            logger.info(
                f"Loaded metadata: {num_patches_total} patches across {len(patch_timestamps)} frames, "
                f"{len(cam_timestamps)} camera frames, "
                f"{len(lidar_timestamps)} lidar frames"
            )
            
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to load metadata: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None

    def _validate_brake_data(self, h5_file) -> None:
        """Validate brake data availability for Magic Formula fitting.

        Raises:
            ValueError: If brake data is missing or insufficient
        """
        if not self.config.validate_brake_data:
            return  # Validation disabled

        # Check if brake key exists
        if self.config.brake_position_key not in h5_file:
            raise ValueError(
                f"Brake data key '{self.config.brake_position_key}' not found in file. "
                f"Required for Magic Formula label extraction. "
                f"Disable with validate_brake_data=False if not using MF labels."
            )

        try:
            # Load brake data
            brake_data = h5_file[self.config.brake_position_key]
            brake_position = brake_data['value'][:]

            # Count samples with brake actuated
            brake_mask = brake_position > self.config.brake_threshold_mm
            brake_count = int(brake_mask.sum())
            total_samples = len(brake_position)
            brake_percentage = (brake_count / total_samples * 100) if total_samples > 0 else 0.0

            # Validate thresholds (100 samples AND 2%)
            if brake_count < self.config.min_brake_samples or brake_percentage < self.config.min_brake_percentage:
                raise ValueError(
                    f"Insufficient brake data: {brake_count}/{total_samples} samples "
                    f"({brake_percentage:.1f}%) have brake actuated (>{self.config.brake_threshold_mm}mm). "
                    f"Required: >={self.config.min_brake_samples} samples AND "
                    f">={self.config.min_brake_percentage}%. "
                    f"File cannot be used for Magic Formula label extraction."
                )

            logger.info(
                f"Brake validation passed: {brake_count}/{total_samples} samples "
                f"({brake_percentage:.1f}%) have brake actuated"
            )

        except KeyError as e:
            raise ValueError(
                f"Failed to read brake data from '{self.config.brake_position_key}': {e}"
            )

    def _build_timestamp_map(self, h5_file) -> Tuple[Optional[cKDTree], Optional[np.ndarray]]:
        """Build timestamp k-d tree."""
        try:
            image_timestamps = h5_file[self.config.cam_ts_key][:]
            if len(image_timestamps) == 0:
                logger.error("No image timestamps found")
                return None, None
            kdtree = cKDTree(image_timestamps.reshape(-1, 1))
            return kdtree, image_timestamps
        except Exception as e:
            logger.error(f"Error building timestamp map: {e}")
            return None, None
    
    def _build_patch_to_list_mapping(self, h5_file) -> Optional[np.ndarray]:
        """Build patch to list mapping."""
        try:
            num_patches_per_list = h5_file[self.config.patch_num_key][:]
            total_patches = int(num_patches_per_list.sum())
            patch_to_list = np.zeros(total_patches, dtype=np.int32)
            
            current_idx = 0
            for list_idx, count in enumerate(num_patches_per_list):
                count = int(count)
                patch_to_list[current_idx:current_idx + count] = list_idx
                current_idx += count
            
            return patch_to_list
        except Exception as e:
            logger.error(f"Error building patch->list mapping: {e}")
            return None
    
    def _process_all_patches(self, f_src, metadata) -> Tuple[List[int], int, int]:
        """Process all patches with streaming writes and progress bar."""
        num_patches = metadata['num_patches']
        num_batches = (num_patches + self.config.batch_size - 1) // self.config.batch_size
        
        dest_file = self._current_dest_file
        
        # Patch-level progress bar
        self.pbar_patches = tqdm(
            total=num_patches,
            desc=f"  Patches",
            unit="patch",
            position=1,
            leave=False,
            bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]'
        )
        
        with h5py.File(dest_file, 'w') as f_dst:
            datasets = self._create_output_datasets(f_dst)

            valid_count = 0
            total_points = 0
            total_skipped = 0
            valid_indices = []

            for batch_idx in range(num_batches):
                start_idx = batch_idx * self.config.batch_size
                end_idx = min(start_idx + self.config.batch_size, num_patches)
                batch_indices = range(start_idx, end_idx)

                batch_results = self._process_batch(f_src, metadata, batch_indices)

                # Collect valid results
                batch_points = []
                batch_start_indices = []
                batch_labels = []
                batch_original_indices = []
                skipped_count = 0

                for idx, result in zip(batch_indices, batch_results):
                    if result is not None:
                        points = result['points']
                        batch_start_indices.append(total_points)
                        batch_points.append(points)
                        batch_labels.append(result['labels'])
                        batch_original_indices.append(result['original_indices'])
                        total_points += len(points)
                        valid_indices.append(idx)
                    else:
                        skipped_count += 1

                # Write batch to disk
                if batch_points:
                    n_valid = len(batch_points)

                    # Concatenate all points in this batch
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
                    valid_count += n_valid

                total_skipped += skipped_count

                # Update progress
                self.pbar_patches.update(len(batch_indices))

                # Update postfix with stats
                if batch_idx % 10 == 0:
                    self.pbar_patches.set_postfix({
                        'valid': valid_count,
                        'skipped': total_skipped,
                        'points': total_points
                    })

            # Write metadata
            self._write_metadata(f_dst, valid_count, num_patches, total_skipped)
            f_dst.attrs['total_points'] = total_points
        
        # Close patch progress bar
        self.pbar_patches.close()
        
        return valid_indices, valid_count, total_skipped
    
    def _create_output_datasets(self, h5_file) -> Dict[str, h5py.Dataset]:
        """Create output datasets based on spec."""
        datasets = {}
        spec = self._get_output_datasets_spec()

        for name, config in spec.items():
            is_variable = config.get('is_variable', False)

            if is_variable:
                # Variable-length data (e.g., points) - 2D array
                datasets[name] = h5_file.create_dataset(
                    name,
                    shape=(0, *config['shape']),
                    maxshape=(None, *config['shape']),
                    dtype=config['dtype'],
                    chunks=(1000, *config['shape']),  # Larger chunks for efficiency
                    compression='gzip',
                    compression_opts=4
                )
            else:
                # Fixed-length per-patch data
                datasets[name] = h5_file.create_dataset(
                    name,
                    shape=(0,) if config['shape'] == () else (0, *config['shape']),
                    maxshape=(None,) if config['shape'] == () else (None, *config['shape']),
                    dtype=config['dtype'],
                    chunks=(100,) if config['shape'] == () else (100, *config['shape']),
                    compression='gzip',
                    compression_opts=4
                )

        return datasets
    
    def _process_batch(self, f_src, metadata, batch_indices: range) -> List[Optional[Dict]]:
        """Process batch of patches."""
        # Group patches by image for efficiency
        patches_by_image = {}
        for patch_idx in batch_indices:
            try:
                image_idx = self._get_image_index(patch_idx, metadata)
                if image_idx not in patches_by_image:
                    patches_by_image[image_idx] = []
                patches_by_image[image_idx].append(patch_idx)
            except Exception as e:
                logger.debug(f"Skipping patch {patch_idx}: {e}")
        
        # Process patches grouped by image
        patch_to_result = {}
        for image_idx, patch_list in patches_by_image.items():
            try:
                rgb_image = self._get_cached_image(image_idx, f_src)

                rgb_image_hwc = rgb_image.permute(1, 2, 0).to(self.device)  # Once per image!
                for patch_idx in patch_list:  # Fixed: iterate only over patches for this image
                    result = self._process_single_patch(patch_idx, image_idx, f_src, metadata, rgb_image_hwc)
                    patch_to_result[patch_idx] = result
            except Exception as e:
                logger.debug(f"Batch error for image {image_idx}: {e}")
                for patch_idx in patch_list:
                    patch_to_result[patch_idx] = None
        
        # Return results in original order
        return [patch_to_result.get(idx) for idx in batch_indices]
    
    def _get_image_index(self, patch_idx: int, metadata) -> int:
        """Get image index for patch."""
        roadpatchlist_idx = metadata['patch_to_list'][patch_idx]
        patch_timestamp = metadata['patch_list_ts'][roadpatchlist_idx]
        _, image_idx = metadata['kdtree'].query(patch_timestamp)
        return int(image_idx)
    
    def _get_cached_image(self, image_idx: int, h5_file) -> torch.Tensor:
        """Get cached or load image."""
        if image_idx in self.image_cache:
            self.image_cache.move_to_end(image_idx)
            return self.image_cache[image_idx]
        
        rgb_image = self._load_and_debayer_image(h5_file, image_idx)
        self.image_cache[image_idx] = rgb_image
        
        if len(self.image_cache) > self.config.max_cache_size:
            self.image_cache.popitem(last=False)
        
        return rgb_image
    
    def _load_and_debayer_image(self, h5_file, image_idx: int) -> torch.Tensor:
        """Load and debayer image."""
        
        bayer_data = safe_h5_index(h5_file[self.config.cam_img_key], image_idx)
        bayer_tensor = torch.from_numpy(bayer_data).float()
        
        if bayer_tensor.dim() == 2:
            bayer_tensor = bayer_tensor.unsqueeze(0)
        
        rgb_tensor = raw_to_rgb(bayer_tensor, CFA.BG)
        rgb_tensor = rgb_tensor / 255.0
        
        return rgb_tensor.squeeze(0).to(self.device)
    
    def _write_metadata(self, h5_file, num_valid: int, num_original: int, num_skipped: int):
        """Write metadata attributes."""
        h5_file.attrs['source_file'] = self._current_source_file
        h5_file.attrs['original_num_patches'] = num_original
        h5_file.attrs['num_valid_patches'] = num_valid
        h5_file.attrs['num_skipped_patches'] = num_skipped
        h5_file.attrs['min_points'] = self.config.min_points
        h5_file.attrs['sensor_model'] = self.config.sensor_model
        h5_file.attrs['max_lidar_range'] = self.config.max_lidar_range


class MagicFormulaPreprocessor(BasePreprocessor):
    """
    Base class for preprocessors using Magic Formula geo-labeling.

    Provides common functionality:
    - OusterLidarNormalizer and RGBNormalizer initialization
    - MagicFormulaGeoExtractor initialization per file
    - Bounds-checked label extraction
    """

    def __init__(self, config: PreprocessConfig):
        self.label_extractor = None
        super().__init__(config)

    def _initialize_tools(self) -> Dict:
        """Initialize common normalizers."""
        logger.info(f"Using device: {self.device}")
        logger.info("Using Magic Formula D parameter fitting from braking data with geospatial matching")

        return {
            'lidar_normalizer': OusterLidarNormalizer(
                sensor_model=self.config.sensor_model,
                max_range=self.config.max_lidar_range
            ),
            'rgb_normalizer': RGBNormalizer()
        }

    def _process_file(self, source_file, dest_file):
        """Override to initialize Magic Formula geo-extractor per file."""
        # Validate brake data BEFORE initializing extractor
        logger.info(f"Validating brake data for {source_file.name}...")
        with h5py.File(source_file, 'r') as f_src:
            self._validate_brake_data(f_src)

        # Initialize label extractor for this file
        logger.info(f"Initializing Magic Formula geo-extractor for {source_file.name}...")
        with h5py.File(source_file, 'r') as f_src:
            self.label_extractor = MagicFormulaGeoExtractor(MagicFormulaGeoConfig())
            if not self.label_extractor.initialize(f_src):
                raise ValueError("Failed to initialize Magic Formula geo-extractor")

        # Call parent's _process_file
        return super()._process_file(source_file, dest_file)

    def _extract_label(self, patch_idx: int) -> Optional[float]:
        """
        Extract label with bounds checking.

        Args:
            patch_idx: Index of the patch in road_patches

        Returns:
            Magic Formula D parameter, or None if:
            - patch_idx is out of bounds for georeferenced data
            - measurement wheel never entered the patch polygon
        """
        if self.label_extractor is None:
            logger.error("Label extractor not initialized!")
            return None

        return self.label_extractor.extract_label(patch_idx)


@dataclass
class IntermediatePreprocessConfig:
    """Configuration for preprocessors that read from intermediate labeled files."""
    # Intermediate labeled files (output of preprocess_labels.py)
    intermediate_folder: str

    # Original source files (for raw data extraction)
    source_folder: str

    # Output destination
    dest_folder: str
    output_suffix: str = "_preprocessed"
    skip_existing: bool = True

    # Processing config
    min_points: int = 100
    image_full_size: Tuple[int, int] = (3032, 5032)
    batch_size: int = 32
    max_cache_size: int = 20

    # HDF5 keys for raw data
    cam_img_key: str = 'hi5/road/image/data'
    lidar_table_key: str = 'hi5/road/lidar_point_cloud/data/all_points'
    lidar_frame_idx_key: str = 'hi5/road/lidar_point_cloud/data/frame_start_indices'
    patch_table_key: str = 'hi5/road/road_patches/pointcloud_data'

    # Model config
    sensor_model: str = "OS-2"
    max_lidar_range: float = 240.0


class IntermediatePreprocessor(ABC):
    """
    Base class for preprocessors that read from intermediate labeled files.

    This approach:
    1. Reads pre-labeled patches from intermediate H5 files (from preprocess_labels.py)
    2. Opens corresponding original H5 files for raw data (images, LiDAR)
    3. Only processes patches that already have valid labels
    4. Avoids redundant Magic Formula fitting and geospatial matching
    """

    def __init__(self, config: IntermediatePreprocessConfig):
        self.config = config
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.image_cache = OrderedDict()
        self.tools = self._initialize_tools()

        # Progress tracking
        self.pbar_files = None
        self.pbar_patches = None

        # Magic Formula parameters (loaded from intermediate files)
        self._mf_attrs = {}

    @abstractmethod
    def _initialize_tools(self) -> Dict:
        """Initialize tools (normalizers, etc.)."""
        pass

    @abstractmethod
    def _get_output_datasets_spec(self) -> Dict[str, Dict]:
        """Specify output dataset structure."""
        pass

    @abstractmethod
    def _process_single_patch(
        self,
        patch_idx: int,
        image_idx: int,
        label: float,
        bbox: np.ndarray,
        f_src,
        rgb_image: torch.Tensor
    ) -> Optional[Dict[str, np.ndarray]]:
        """Process single patch (feature extraction only, label already provided)."""
        pass

    def run(self):
        """Execute preprocessing for all intermediate files."""
        print("\n" + "="*80)
        print("FEATURE PREPROCESSING STARTED")
        print("="*80)

        intermediate_path = Path(self.config.intermediate_folder)
        source_path = Path(self.config.source_folder)
        dest_path = Path(self.config.dest_folder)
        dest_path.mkdir(parents=True, exist_ok=True)

        print(f"Intermediate: {intermediate_path}")
        print(f"Source:       {source_path}")
        print(f"Dest:         {dest_path}")
        print(f"Device:       {self.device}")

        intermediate_files = self._discover_intermediate_files(intermediate_path)

        if not intermediate_files:
            logger.warning(f"No H5 files found in {intermediate_path}")
            return

        print(f"\nFound {len(intermediate_files)} intermediate files to process:")
        for i, f in enumerate(intermediate_files, 1):
            print(f"  {i}. {f.name}")
        print("="*80 + "\n")

        self.pbar_files = tqdm(
            total=len(intermediate_files),
            desc="Files",
            unit="file",
            position=0,
            leave=True,
            bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]'
        )

        successful = 0
        failed = 0

        for intermediate_file in intermediate_files:
            # Find corresponding source file
            source_file = self._find_source_file(intermediate_file, source_path)
            if source_file is None:
                self.pbar_files.write(f"  {intermediate_file.name}: Source file not found")
                failed += 1
                self.pbar_files.update(1)
                continue

            dest_file = self._get_output_path(intermediate_file, dest_path)
            self.pbar_files.set_description(f"Files [{intermediate_file.name}]")

            if self.config.skip_existing and dest_file.exists():
                self.pbar_files.write(f"  Skipping {intermediate_file.name} (already exists)")
                self.pbar_files.update(1)
                successful += 1
                continue

            try:
                processed, skipped = self._process_file(intermediate_file, source_file, dest_file)
                self.pbar_files.write(
                    f"  {intermediate_file.name}: {processed} processed, {skipped} skipped"
                )
                successful += 1
            except Exception as e:
                self.pbar_files.write(f"  {intermediate_file.name}: {str(e)}")
                logger.exception(e)
                failed += 1

                if dest_file.exists():
                    dest_file.unlink()

            self.pbar_files.update(1)
            self.image_cache.clear()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

        self.pbar_files.close()

        print("\n" + "="*80)
        print("FEATURE PREPROCESSING COMPLETE")
        print(f"  Total:      {len(intermediate_files)}")
        print(f"  Successful: {successful}")
        print(f"  Failed:     {failed}")
        print("="*80 + "\n")

    def _discover_intermediate_files(self, intermediate_path: Path) -> List[Path]:
        """Discover all H5 files in intermediate folder."""
        files = list(intermediate_path.glob("*.h5"))
        return sorted(files)

    def _find_source_file(self, intermediate_file: Path, source_path: Path) -> Optional[Path]:
        """Find the original source file for an intermediate file."""
        # Remove _labeled suffix to get original filename
        original_stem = intermediate_file.stem.replace("_labeled", "")
        source_file = source_path / f"{original_stem}.h5"

        if source_file.exists():
            return source_file
        return None

    def _get_output_path(self, intermediate_file: Path, dest_folder: Path) -> Path:
        """Generate output path."""
        original_stem = intermediate_file.stem.replace("_labeled", "")
        output_name = f"{original_stem}{self.config.output_suffix}.h5"
        return dest_folder / output_name

    def _process_file(
        self,
        intermediate_file: Path,
        source_file: Path,
        dest_file: Path
    ) -> Tuple[int, int]:
        """Process single file using intermediate labels."""
        self._current_source_file = source_file.name
        self._current_dest_file = dest_file

        # Load intermediate data (labels, bboxes, image_indices)
        with h5py.File(intermediate_file, 'r') as f_int:
            patch_indices = f_int['patch_indices'][:]
            labels = f_int['labels'][:]
            bboxes = f_int['bounding_boxes'][:]
            image_indices = f_int['image_indices'][:]

            # Load all Magic Formula parameters from intermediate file
            self._mf_attrs = {}
            for attr_name in f_int.attrs.keys():
                if attr_name.startswith('mf_'):
                    self._mf_attrs[attr_name] = f_int.attrs[attr_name]

            logger.info(f"Loaded {len(patch_indices)} labeled patches from intermediate file")
            if 'mf_D' in self._mf_attrs:
                logger.info(f"MF D parameter: {self._mf_attrs['mf_D']:.3f}")

        # Process patches using source file for raw data
        with h5py.File(source_file, 'r') as f_src:
            processed, skipped = self._process_all_patches(
                f_src, patch_indices, labels, bboxes, image_indices
            )

        return processed, skipped

    def _process_all_patches(
        self,
        f_src,
        patch_indices: np.ndarray,
        labels: np.ndarray,
        bboxes: np.ndarray,
        image_indices: np.ndarray
    ) -> Tuple[int, int]:
        """Process all pre-labeled patches."""
        num_patches = len(patch_indices)
        num_batches = (num_patches + self.config.batch_size - 1) // self.config.batch_size

        dest_file = self._current_dest_file

        self.pbar_patches = tqdm(
            total=num_patches,
            desc="  Patches",
            unit="patch",
            position=1,
            leave=False,
            bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]'
        )

        with h5py.File(dest_file, 'w') as f_dst:
            datasets = self._create_output_datasets(f_dst)

            valid_count = 0
            total_skipped = 0

            for batch_idx in range(num_batches):
                start_idx = batch_idx * self.config.batch_size
                end_idx = min(start_idx + self.config.batch_size, num_patches)

                batch_results = self._process_batch(
                    f_src,
                    patch_indices[start_idx:end_idx],
                    labels[start_idx:end_idx],
                    bboxes[start_idx:end_idx],
                    image_indices[start_idx:end_idx]
                )

                # Write batch results
                n_valid, n_skipped = self._write_batch_results(
                    f_dst, datasets, batch_results, valid_count
                )
                valid_count += n_valid
                total_skipped += n_skipped

                self.pbar_patches.update(end_idx - start_idx)

                if batch_idx % 10 == 0:
                    self.pbar_patches.set_postfix({
                        'valid': valid_count,
                        'skipped': total_skipped
                    })

            self._write_metadata(f_dst, valid_count, num_patches, total_skipped)

        self.pbar_patches.close()
        return valid_count, total_skipped

    def _process_batch(
        self,
        f_src,
        patch_indices: np.ndarray,
        labels: np.ndarray,
        bboxes: np.ndarray,
        image_indices: np.ndarray
    ) -> List[Optional[Dict]]:
        """Process batch of patches grouped by image for efficiency."""
        # Group patches by image
        patches_by_image = {}
        for i, image_idx in enumerate(image_indices):
            if image_idx not in patches_by_image:
                patches_by_image[image_idx] = []
            patches_by_image[image_idx].append(i)

        # Process patches grouped by image
        results = [None] * len(patch_indices)

        for image_idx, local_indices in patches_by_image.items():
            try:
                rgb_image = self._get_cached_image(int(image_idx), f_src)
                rgb_image_hwc = rgb_image.permute(1, 2, 0).to(self.device)

                for local_idx in local_indices:
                    result = self._process_single_patch(
                        int(patch_indices[local_idx]),
                        int(image_idx),
                        float(labels[local_idx]),
                        bboxes[local_idx],
                        f_src,
                        rgb_image_hwc
                    )
                    results[local_idx] = result
            except Exception as e:
                logger.debug(f"Batch error for image {image_idx}: {e}")

        return results

    @abstractmethod
    def _write_batch_results(
        self,
        f_dst,
        datasets: Dict,
        batch_results: List[Optional[Dict]],
        valid_count: int
    ) -> Tuple[int, int]:
        """Write batch results to output file. Returns (n_valid, n_skipped)."""
        pass

    def _create_output_datasets(self, h5_file) -> Dict[str, h5py.Dataset]:
        """Create output datasets based on spec."""
        datasets = {}
        spec = self._get_output_datasets_spec()

        for name, config in spec.items():
            is_variable = config.get('is_variable', False)

            if is_variable:
                datasets[name] = h5_file.create_dataset(
                    name,
                    shape=(0, *config['shape']),
                    maxshape=(None, *config['shape']),
                    dtype=config['dtype'],
                    chunks=(1000, *config['shape']),
                    compression='gzip',
                    compression_opts=4
                )
            else:
                shape = (0,) if config['shape'] == () else (0, *config['shape'])
                maxshape = (None,) if config['shape'] == () else (None, *config['shape'])
                chunks = (100,) if config['shape'] == () else (100, *config['shape'])

                datasets[name] = h5_file.create_dataset(
                    name,
                    shape=shape,
                    maxshape=maxshape,
                    dtype=config['dtype'],
                    chunks=chunks,
                    compression='gzip',
                    compression_opts=4
                )

        return datasets

    def _get_cached_image(self, image_idx: int, h5_file) -> torch.Tensor:
        """Get cached or load image."""
        if image_idx in self.image_cache:
            self.image_cache.move_to_end(image_idx)
            return self.image_cache[image_idx]

        rgb_image = self._load_and_debayer_image(h5_file, image_idx)
        self.image_cache[image_idx] = rgb_image

        if len(self.image_cache) > self.config.max_cache_size:
            self.image_cache.popitem(last=False)

        return rgb_image

    def _load_and_debayer_image(self, h5_file, image_idx: int) -> torch.Tensor:
        """Load and debayer image."""
        bayer_data = safe_h5_index(h5_file[self.config.cam_img_key], image_idx)
        bayer_tensor = torch.from_numpy(bayer_data).float()

        if bayer_tensor.dim() == 2:
            bayer_tensor = bayer_tensor.unsqueeze(0)

        rgb_tensor = raw_to_rgb(bayer_tensor, CFA.BG)
        rgb_tensor = rgb_tensor / 255.0

        return rgb_tensor.squeeze(0).to(self.device)

    def _write_metadata(self, h5_file, num_valid: int, num_original: int, num_skipped: int):
        """Write metadata attributes."""
        h5_file.attrs['source_file'] = self._current_source_file
        h5_file.attrs['original_num_patches'] = num_original
        h5_file.attrs['num_valid_patches'] = num_valid
        h5_file.attrs['num_skipped_patches'] = num_skipped
        h5_file.attrs['sensor_model'] = self.config.sensor_model
        h5_file.attrs['max_lidar_range'] = self.config.max_lidar_range

        # Copy Magic Formula parameters from intermediate file
        if hasattr(self, '_mf_attrs'):
            for attr_name, attr_value in self._mf_attrs.items():
                h5_file.attrs[attr_name] = attr_value


