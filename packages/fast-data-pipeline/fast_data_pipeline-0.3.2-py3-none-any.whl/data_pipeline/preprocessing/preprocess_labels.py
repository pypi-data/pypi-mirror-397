"""
Intermediate preprocessing: Generate labeled patches with geospatial filtering.

This preprocessing step:
1. Validates brake data availability
2. Fits Magic Formula tire model from braking wheel dynamics
3. Filters patches to only georeferenced ones
4. Performs point-in-polygon testing (measurement wheel trajectory)
5. Writes intermediate H5 with only valid labeled patches

Output structure:
- patch_indices: Original indices from road_patches
- labels: Magic Formula D parameter
- bounding_boxes: (N, 4) - top_left_u, top_left_v, bottom_right_u, bottom_right_v
- image_indices: Camera frame index for each patch
- source_file: Reference to original H5 file

Model-specific preprocessors (preprocess_pointcloud, preprocess_spconv) then read
from these intermediate files, avoiding redundant MF fitting and geospatial filtering.
"""
import h5py
import numpy as np
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass
import logging
import glob
from tqdm import tqdm
from scipy.spatial import cKDTree

from data_pipeline.preprocessing.label_extractors import MagicFormulaGeoExtractor, MagicFormulaGeoConfig

logger = logging.getLogger(__name__)


@dataclass
class LabelPreprocessConfig:
    """Configuration for label preprocessing."""
    source_folder: str
    dest_folder: str
    source_pattern: str = "*.h5"
    output_suffix: str = "_labeled"
    skip_existing: bool = True

    # HDF5 keys for road patches
    patch_table_key: str = 'hi5/road/road_patches/pointcloud_data'
    patch_num_key: str = 'hi5/road/road_patches/num_patches'
    patch_ts_s_key: str = 'hi5/road/road_patches/timestamp/timestamp_s'
    patch_ts_ns_key: str = 'hi5/road/road_patches/timestamp/timestamp_ns'

    # Camera timestamps for patch-to-image mapping
    cam_ts_s_key: str = 'hi5/road/image/timestamp/timestamp_s'
    cam_ts_ns_key: str = 'hi5/road/image/timestamp/timestamp_ns'

    # Brake data validation
    brake_position_key: str = "rfmu/vehicle_data/brake_actuator_position_mm"
    brake_threshold_mm: float = 1.0
    min_brake_samples: int = 100
    min_brake_percentage: float = 2.0


class LabelPreprocessor:
    """
    Preprocessor that generates intermediate H5 files with labeled patches.

    Centralizes:
    - Magic Formula fitting (runs once per file)
    - Geospatial filtering (point-in-polygon testing)
    - Patch validity checks

    Output files can then be used by model-specific preprocessors without
    duplicating the expensive MF fitting and geospatial matching logic.
    """

    def __init__(self, config: LabelPreprocessConfig):
        self.config = config
        self.label_extractor: Optional[MagicFormulaGeoExtractor] = None

    @staticmethod
    def combine_timestamps(ts_s: np.ndarray, ts_ns: np.ndarray) -> np.ndarray:
        """Combine seconds and nanoseconds into precise timestamp."""
        return ts_s.astype(np.float64) + ts_ns.astype(np.float64) * 1e-9

    def run(self):
        """Execute label preprocessing for all files."""
        print("\n" + "="*80)
        print("LABEL PREPROCESSING STARTED")
        print("="*80)

        source_path = Path(self.config.source_folder)
        dest_path = Path(self.config.dest_folder)
        dest_path.mkdir(parents=True, exist_ok=True)

        print(f"Source: {source_path}")
        print(f"Dest:   {dest_path}")

        h5_files = self._discover_files(source_path)

        if not h5_files:
            logger.warning(f"No files matching '{self.config.source_pattern}' found")
            return

        print(f"\nFound {len(h5_files)} files to process:")
        for i, f in enumerate(h5_files, 1):
            size_mb = f.stat().st_size / (1024 * 1024)
            print(f"  {i}. {f.name} ({size_mb:.1f} MB)")
        print("="*80 + "\n")

        pbar_files = tqdm(
            total=len(h5_files),
            desc="Files",
            unit="file",
            position=0,
            leave=True,
            bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]'
        )

        successful = 0
        failed = 0
        total_labeled = 0
        total_skipped = 0

        for source_file in h5_files:
            dest_file = self._get_output_path(source_file, dest_path)
            pbar_files.set_description(f"Files [{source_file.name}]")

            if self.config.skip_existing and dest_file.exists():
                pbar_files.write(f"  Skipping {source_file.name} (already exists)")
                pbar_files.update(1)
                successful += 1
                continue

            try:
                labeled, skipped = self._process_file(source_file, dest_file)
                pbar_files.write(
                    f"  {source_file.name}: {labeled} labeled, {skipped} skipped"
                )
                successful += 1
                total_labeled += labeled
                total_skipped += skipped
            except Exception as e:
                pbar_files.write(f"  {source_file.name}: FAILED - {str(e)}")
                logger.exception(e)
                failed += 1

                if dest_file.exists():
                    dest_file.unlink()

            pbar_files.update(1)

        pbar_files.close()

        print("\n" + "="*80)
        print("LABEL PREPROCESSING COMPLETE")
        print(f"  Files processed: {successful}/{len(h5_files)}")
        print(f"  Files failed:    {failed}")
        print(f"  Total labeled:   {total_labeled}")
        print(f"  Total skipped:   {total_skipped}")
        print("="*80 + "\n")

    def _discover_files(self, source_path: Path) -> List[Path]:
        """Discover H5 files."""
        pattern = str(source_path / self.config.source_pattern)
        files = [Path(f) for f in glob.glob(pattern)]
        # Exclude already processed files
        files = [f for f in files if self.config.output_suffix not in f.stem]
        files = [f for f in files if "_preprocessed" not in f.stem]
        return sorted(files)

    def _get_output_path(self, source_file: Path, dest_folder: Path) -> Path:
        """Generate output path."""
        output_name = f"{source_file.stem}{self.config.output_suffix}.h5"
        return dest_folder / output_name

    def _validate_brake_data(self, h5_file) -> bool:
        """Validate brake data availability for Magic Formula fitting."""
        if self.config.brake_position_key not in h5_file:
            logger.error(f"Brake data key '{self.config.brake_position_key}' not found")
            return False

        try:
            brake_data = h5_file[self.config.brake_position_key]
            brake_position = brake_data['value'][:]

            brake_mask = brake_position > self.config.brake_threshold_mm
            brake_count = int(brake_mask.sum())
            total_samples = len(brake_position)
            brake_percentage = (brake_count / total_samples * 100) if total_samples > 0 else 0.0

            if brake_count < self.config.min_brake_samples or brake_percentage < self.config.min_brake_percentage:
                logger.error(
                    f"Insufficient brake data: {brake_count}/{total_samples} samples "
                    f"({brake_percentage:.1f}%) have brake actuated"
                )
                return False

            logger.info(
                f"Brake validation passed: {brake_count}/{total_samples} samples "
                f"({brake_percentage:.1f}%) have brake actuated"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to validate brake data: {e}")
            return False

    def _process_file(self, source_file: Path, dest_file: Path) -> Tuple[int, int]:
        """Process single file: validate, fit MF, extract labels."""
        with h5py.File(source_file, 'r') as f_src:
            # Step 1: Validate brake data
            if not self._validate_brake_data(f_src):
                raise ValueError("Brake data validation failed")

            # Step 2: Initialize Magic Formula geo-extractor
            logger.info("Initializing Magic Formula geo-extractor...")
            self.label_extractor = MagicFormulaGeoExtractor(MagicFormulaGeoConfig())
            if not self.label_extractor.initialize(f_src):
                raise ValueError("Failed to initialize Magic Formula geo-extractor")

            # Step 3: Load patch metadata
            patch_table = f_src[self.config.patch_table_key]
            num_patches = patch_table.shape[0]

            # Build patch-to-image mapping
            patch_ts_s = f_src[self.config.patch_ts_s_key][:]
            patch_ts_ns = f_src[self.config.patch_ts_ns_key][:]
            patch_timestamps = self.combine_timestamps(patch_ts_s, patch_ts_ns)

            cam_ts_s = f_src[self.config.cam_ts_s_key][:]
            cam_ts_ns = f_src[self.config.cam_ts_ns_key][:]
            cam_timestamps = self.combine_timestamps(cam_ts_s, cam_ts_ns)

            # Build patch-to-frame mapping
            num_patches_per_frame = f_src[self.config.patch_num_key][:]
            patch_start_indices = np.concatenate([[0], np.cumsum(num_patches_per_frame)])

            patch_to_frame = np.zeros(num_patches, dtype=np.int32)
            for frame_idx in range(len(num_patches_per_frame)):
                start_idx = patch_start_indices[frame_idx]
                end_idx = patch_start_indices[frame_idx + 1]
                if end_idx > num_patches:
                    end_idx = num_patches
                if start_idx < num_patches:
                    patch_to_frame[start_idx:end_idx] = frame_idx

            # KD-tree for camera timestamp lookup
            kdtree = cKDTree(cam_timestamps.reshape(-1, 1))

            # Step 4: Process all patches - extract labels with geospatial matching
            valid_patches = []
            valid_labels = []
            valid_bboxes = []
            valid_image_indices = []

            pbar = tqdm(
                total=num_patches,
                desc="  Extracting labels",
                unit="patch",
                position=1,
                leave=False
            )

            for patch_idx in range(num_patches):
                # Extract label using geospatial matching (point-in-polygon)
                label = self.label_extractor.extract_label(patch_idx)

                if label is not None:
                    # Get patch bounding box
                    patch_row = patch_table[patch_idx]
                    bbox = np.array([
                        int(patch_row['top_left_u']),
                        int(patch_row['top_left_v']),
                        int(patch_row['bottom_right_u']),
                        int(patch_row['bottom_right_v'])
                    ], dtype=np.int32)

                    # Get image index
                    frame_idx = patch_to_frame[patch_idx]
                    frame_ts = patch_timestamps[frame_idx] if frame_idx < len(patch_timestamps) else patch_timestamps[-1]
                    _, image_idx = kdtree.query(frame_ts)

                    valid_patches.append(patch_idx)
                    valid_labels.append(label)
                    valid_bboxes.append(bbox)
                    valid_image_indices.append(int(image_idx))

                pbar.update(1)
                if patch_idx % 1000 == 0:
                    pbar.set_postfix({'valid': len(valid_patches)})

            pbar.close()

            num_labeled = len(valid_patches)
            num_skipped = num_patches - num_labeled

            logger.info(f"Labeled {num_labeled}/{num_patches} patches ({num_skipped} skipped)")

        # Step 5: Write intermediate H5 file
        if num_labeled > 0:
            self._write_intermediate_file(
                dest_file,
                source_file.name,
                valid_patches,
                valid_labels,
                valid_bboxes,
                valid_image_indices,
                num_patches
            )
        else:
            raise ValueError("No valid patches found after geospatial filtering")

        return num_labeled, num_skipped

    def _write_intermediate_file(
        self,
        dest_file: Path,
        source_filename: str,
        patch_indices: List[int],
        labels: List[float],
        bboxes: List[np.ndarray],
        image_indices: List[int],
        original_num_patches: int
    ):
        """Write intermediate H5 file with labeled patches."""
        with h5py.File(dest_file, 'w') as f_dst:
            n = len(patch_indices)

            # Store patch indices (original indices from road_patches)
            f_dst.create_dataset(
                'patch_indices',
                data=np.array(patch_indices, dtype=np.int32),
                compression='gzip'
            )

            # Store labels
            f_dst.create_dataset(
                'labels',
                data=np.array(labels, dtype=np.float32),
                compression='gzip'
            )

            # Store bounding boxes (N, 4): top_left_u, top_left_v, bottom_right_u, bottom_right_v
            f_dst.create_dataset(
                'bounding_boxes',
                data=np.array(bboxes, dtype=np.int32),
                compression='gzip'
            )

            # Store image indices
            f_dst.create_dataset(
                'image_indices',
                data=np.array(image_indices, dtype=np.int32),
                compression='gzip'
            )

            # Metadata
            f_dst.attrs['source_file'] = source_filename
            f_dst.attrs['original_num_patches'] = original_num_patches
            f_dst.attrs['num_labeled_patches'] = n

            # Store all Magic Formula parameters
            for param_name, param_value in self.label_extractor._mf_params.items():
                f_dst.attrs[f'mf_{param_name}'] = param_value

            # Store standard deviations (uncertainties)
            for std_name, std_value in self.label_extractor._mf_std.items():
                if std_value is not None:
                    f_dst.attrs[f'mf_{std_name}'] = std_value

            logger.info(f"Wrote {n} labeled patches to {dest_file}")


def preprocess_labels(config: Optional[LabelPreprocessConfig] = None):
    """Main entry point for label preprocessing."""
    if config is None:
        config = LabelPreprocessConfig(
            source_folder="/mnt/Workspace_encrypted/new_rosbags/2025-12-03/synchronized",
            dest_folder="/home/uggld/Desktop/trfc_estimation_camera/data/intermediate/labeled"
        )

    preprocessor = LabelPreprocessor(config)
    preprocessor.run()


if __name__ == "__main__":
    preprocess_labels()
