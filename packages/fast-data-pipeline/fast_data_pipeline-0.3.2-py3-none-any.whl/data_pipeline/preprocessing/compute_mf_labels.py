"""
Precompute Magic Formula D parameter labels for HDF5 files.

This script processes raw HDF5 files and computes the D parameter (peak friction)
from wheel dynamics data using Magic Formula curve fitting.

Usage:
    python -m src.data.preprocessing.compute_mf_labels \
        --source_folder /path/to/raw/h5 \
        --output_key rfmu/magic_formula/D \
        --method svi
"""

import argparse
import logging
from pathlib import Path
from typing import Optional
import glob

import h5py
import numpy as np
from tqdm import tqdm

from data_pipeline.preprocessing.label_extractors import MagicFormulaLabelExtractor, MagicFormulaConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def compute_mf_labels_for_file(
    h5_path: Path,
    extractor: MagicFormulaLabelExtractor,
    output_key: str,
    method: str = "svi",
    window_size: Optional[int] = None
) -> bool:
    """Compute Magic Formula D parameter for a single HDF5 file.

    Args:
        h5_path: Path to HDF5 file
        extractor: Magic Formula label extractor
        output_key: HDF5 key to store D parameter
        method: Fitting method - "svi" or "nelder"
        window_size: If provided, compute D per window. Otherwise compute per file.

    Returns:
        True if successful, False otherwise
    """
    try:
        with h5py.File(h5_path, 'r+') as f:
            # Check if required data exists
            config = extractor.config
            required_keys = [
                config.wheel_angular_velocity_key,
                config.vehicle_velocity_key,
                config.wheel_force_x_key,
                config.wheel_force_z_key
            ]

            for key in required_keys:
                if key not in f:
                    logger.error(f"Missing required key {key} in {h5_path}")
                    return False

            if window_size is None:
                # Compute single D value for entire file
                d_param = extractor.extract_from_h5(f, method=method)

                # Create or update output dataset
                if output_key in f:
                    del f[output_key]

                f.create_dataset(output_key, data=np.array([d_param]))
                logger.info(f"Computed D={d_param:.4f} for {h5_path.name}")

            else:
                # Compute D values per window
                data_len = len(f[config.wheel_angular_velocity_key])
                num_windows = (data_len + window_size - 1) // window_size

                d_params = []
                for i in range(num_windows):
                    start_idx = i * window_size
                    end_idx = min((i + 1) * window_size, data_len)

                    d_param = extractor.extract_from_h5(
                        f,
                        start_idx=start_idx,
                        end_idx=end_idx,
                        method=method
                    )
                    d_params.append(d_param)

                # Create or update output dataset
                if output_key in f:
                    del f[output_key]

                f.create_dataset(output_key, data=np.array(d_params))
                logger.info(f"Computed {len(d_params)} D values for {h5_path.name}")

        return True

    except Exception as e:
        logger.error(f"Failed to process {h5_path}: {e}")
        return False


def compute_per_frame_labels(
    h5_path: Path,
    extractor: MagicFormulaLabelExtractor,
    output_key: str,
    method: str = "svi",
    context_window: int = 100
) -> bool:
    """Compute Magic Formula D parameter per frame with sliding context window.

    This computes a D value for each timestamp by fitting to surrounding data points.

    Args:
        h5_path: Path to HDF5 file
        extractor: Magic Formula label extractor
        output_key: HDF5 key to store D parameters
        method: Fitting method - "svi" or "nelder"
        context_window: Number of samples before and after each frame to use

    Returns:
        True if successful, False otherwise
    """
    try:
        with h5py.File(h5_path, 'r+') as f:
            config = extractor.config

            # Load all data
            wheel_angular_velocity = f[config.wheel_angular_velocity_key][:]
            vehicle_velocity = f[config.vehicle_velocity_key][:]
            wheel_force_x = f[config.wheel_force_x_key][:]
            wheel_force_z = f[config.wheel_force_z_key][:]

            data_len = len(wheel_angular_velocity)
            d_params = np.zeros(data_len)

            # Compute slip and friction once for entire file
            slip, friction = extractor.compute_slip_and_friction(
                wheel_angular_velocity,
                vehicle_velocity,
                wheel_force_x,
                wheel_force_z
            )

            # Fit for each frame with context window
            for i in tqdm(range(data_len), desc=f"Computing D for {h5_path.name}"):
                start_idx = max(0, i - context_window)
                end_idx = min(data_len, i + context_window + 1)

                window_slip = slip[start_idx:end_idx]
                window_friction = friction[start_idx:end_idx]

                # Filter valid values
                valid_mask = np.isfinite(window_slip) & np.isfinite(window_friction)
                if np.sum(valid_mask) < 50:
                    d_params[i] = np.nan
                    continue

                try:
                    results = extractor.fit_magic_formula(
                        window_slip[valid_mask],
                        window_friction[valid_mask]
                    )
                    d_params[i] = results[method]["parameters"].D
                except Exception:
                    d_params[i] = np.nan

            # Create or update output dataset
            if output_key in f:
                del f[output_key]

            f.create_dataset(output_key, data=d_params)
            valid_count = np.sum(np.isfinite(d_params))
            logger.info(f"Computed {valid_count}/{data_len} valid D values for {h5_path.name}")

        return True

    except Exception as e:
        logger.error(f"Failed to process {h5_path}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Compute Magic Formula D parameter labels")
    parser.add_argument("--source_folder", required=True, help="Folder containing HDF5 files")
    parser.add_argument("--output_key", default="rfmu/magic_formula/D",
                        help="HDF5 key to store computed D parameter")
    parser.add_argument("--method", choices=["svi", "nelder"], default="svi",
                        help="Fitting method to use")
    parser.add_argument("--pattern", default="*.h5", help="File pattern to match")
    parser.add_argument("--per_frame", action="store_true",
                        help="Compute D per frame instead of per file")
    parser.add_argument("--context_window", type=int, default=100,
                        help="Context window size for per-frame computation")
    parser.add_argument("--window_size", type=int, default=None,
                        help="Window size for segmented computation (not per-frame)")

    # Custom HDF5 keys
    parser.add_argument("--wheel_angular_velocity_key",
                        default="rfmu/wheel/angular_velocity_radps")
    parser.add_argument("--vehicle_velocity_key",
                        default="hi5/velocity/x_mps")
    parser.add_argument("--wheel_force_x_key",
                        default="rfmu/wheel/force_x_N")
    parser.add_argument("--wheel_force_z_key",
                        default="rfmu/wheel/force_z_N")

    args = parser.parse_args()

    # Create config
    config = MagicFormulaConfig(
        wheel_angular_velocity_key=args.wheel_angular_velocity_key,
        vehicle_velocity_key=args.vehicle_velocity_key,
        wheel_force_x_key=args.wheel_force_x_key,
        wheel_force_z_key=args.wheel_force_z_key
    )
    extractor = MagicFormulaLabelExtractor(config)

    # Find files
    source_path = Path(args.source_folder)
    pattern = str(source_path / args.pattern)
    h5_files = sorted([Path(f) for f in glob.glob(pattern)])

    if not h5_files:
        logger.error(f"No files matching {pattern}")
        return

    logger.info(f"Found {len(h5_files)} files to process")

    # Process files
    successful = 0
    failed = 0

    for h5_path in tqdm(h5_files, desc="Processing files"):
        if args.per_frame:
            success = compute_per_frame_labels(
                h5_path,
                extractor,
                args.output_key,
                args.method,
                args.context_window
            )
        else:
            success = compute_mf_labels_for_file(
                h5_path,
                extractor,
                args.output_key,
                args.method,
                args.window_size
            )

        if success:
            successful += 1
        else:
            failed += 1

    logger.info(f"Complete: {successful} successful, {failed} failed")


if __name__ == "__main__":
    main()
