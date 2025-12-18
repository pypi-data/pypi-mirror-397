"""Label extraction utilities for friction coefficient estimation with geospatial synchronization."""

import logging
from dataclasses import dataclass
from typing import Optional
import numpy as np
from omegaconf import OmegaConf
from scipy.spatial import cKDTree

# Import submodule components
from magic_formula_fitting import fit_tire_parameters
from magic_formula_fitting.fitting_algorithms import tire_param_fitting
from magic_formula_fitting.parameters import MFSimpleParams

logger = logging.getLogger(__name__)


def calc_force_shift_adaptive(sigma: np.array, force_n: np.array, sigma_bound: float = 0.015):
    """Adaptive version of calc_force_shift that handles wider slip ranges.

    This is a local override of the submodule's calc_force_shift to handle braking data.
    """
    mask = np.abs(sigma) <= sigma_bound
    if not np.any(mask):
        # Fallback: use progressively wider bounds until we find data
        for fallback_bound in [0.05, 0.10, 0.15, 0.20]:
            mask = np.abs(sigma) <= fallback_bound
            if np.any(mask):
                logger.warning(f"No data within sigma_bound={sigma_bound:.3f}, "
                              f"using fallback={fallback_bound:.3f}")
                sigma_bound = fallback_bound
                break
        else:
            raise ValueError(f"No values within any sigma bound up to 0.20. "
                           f"Slip range: [{sigma.min():.3f}, {sigma.max():.3f}]")

    coeff = np.polyfit(sigma[mask], force_n[mask], 1)
    horizontal_shift = float(np.roots(coeff)[0].real / 2)
    vertical_shift = float(np.polyval(coeff, 0) / 2)
    return vertical_shift, horizontal_shift


def fit_tire_parameters_custom(
    force_n: np.array,
    load_n: np.array,
    sigma: np.array,
    config: OmegaConf,
    fit_flags: dict,
):
    """Custom tire parameter fitting that uses adaptive sigma bounds.

    This wraps the submodule's fit_tire_parameters with our adaptive calc_force_shift.
    """
    params_min = MFSimpleParams(**config.params_min)
    params_max = MFSimpleParams(**config.params_max)
    params_init = MFSimpleParams(**config.params_init)

    # Use our adaptive version instead of submodule's calc_force_shift
    sigma_bound = config.get('sigma_bound', 0.015)
    params_init.S_V, params_init.S_H = calc_force_shift_adaptive(sigma, force_n, sigma_bound)
    # D is friction coefficient (dimensionless), not force
    # Compute as max(force/load) to get peak friction coefficient
    params_init.D = np.max(force_n / load_n)

    # Use submodule's tire_param_fitting for the actual optimization
    params_svi, std_svi, _ = tire_param_fitting(
        "SVI", "MFSimple", sigma, force_n, load_n, params_init, params_min, params_max,
        config.svi_options, fit_flags
    )
    params_nelder, _, _ = tire_param_fitting(
        "Nelder", "MFSimple", sigma, force_n, load_n, params_init, params_min, params_max,
        config.nelder_options, fit_flags
    )

    results = {
        "svi": {"parameters": params_svi, "std": std_svi},
        "nelder": {"parameters": params_nelder, "std": None},
        "params_min": params_min,
        "params_max": params_max,
        "params_init": params_init,
    }

    return results


@dataclass
class MagicFormulaGeoConfig:
    """Configuration for Magic Formula calculation with geospatial synchronization."""

    # Georeferenced road patch keys
    patch_table_key: str = "hi5/road/road_patches_georeferenced/pointcloud_data"
    polygon_points_key: str = "hi5/road/road_patches_georeferenced/polygons/points"
    polygon_start_indices_key: str = "hi5/road/road_patches_georeferenced/polygons/start_indices"
    patch_ts_s_key: str = "hi5/road/road_patches_georeferenced/timestamp/timestamp_s"
    patch_ts_ns_key: str = "hi5/road/road_patches_georeferenced/timestamp/timestamp_ns"
    num_patches_key: str = "hi5/road/road_patches_georeferenced/num_patches"

    # Vehicle GPS trajectory keys
    vehicle_lat_key: str = "hi5/vehicle_data/latitude_center_rear_axle_deg"
    vehicle_lon_key: str = "hi5/vehicle_data/longitude_center_rear_axle_deg"
    vehicle_alt_key: str = "hi5/vehicle_data/altitude_center_rear_axle_m"

    # Measurement wheel GPS and dynamics keys
    mw_lat_key: str = "rfmu/vehicle_data/measurement_wheel_latitude_deg"
    mw_lon_key: str = "rfmu/vehicle_data/measurement_wheel_longitude_deg"
    mw_angular_velocity_key: str = "rfmu/vehicle_data/measurement_wheel_angular_velocity_mabx2_radps"
    vehicle_velocity_key: str = "hi5/vehicle_data/velocity_x_center_rear_axle_mps"
    wheel_force_x_key: str = "rfmu/vehicle_data/measurement_wheel_force_x_N"
    wheel_force_z_key: str = "rfmu/vehicle_data/measurement_wheel_force_z_N"
    mw_timestamp_key: str = "rfmu/vehicle_data/timestamp_s"

    # Magic Formula parameters
    wheel_radius: float = 0.2447891  # meters

    # MF fitting parameters
    nelder_options: dict = None
    svi_options: dict = None
    params_min: dict = None
    params_max: dict = None
    params_init: dict = None
    fit_flags: dict = None

    # Sigma bound for calc_force_shift (increased from default 0.015 to handle braking data)
    sigma_bound: float = 0.10  # 10% slip range (vs original 1.5%)

    # Lane filtering parameters
    max_lateral_distance: float = 2.5  # Maximum lateral distance from vehicle trajectory (meters)
    trajectory_smoothing_window: int = 10  # Smoothing window for trajectory (samples)

    # Geospatial matching parameters
    max_spatial_distance: float = 10.0  # Maximum distance for spatial matching (meters)
    max_temporal_distance: float = 2.0  # Maximum time difference for matching (seconds)

    # Brake filtering parameters (always enabled)
    brake_position_key: str = "rfmu/vehicle_data/brake_actuator_position_mm"
    brake_threshold_mm: float = 1.0  # Minimum brake position to count as braking

    def __post_init__(self):
        """Set default MF fitting parameters if not provided."""
        if self.nelder_options is None:
            self.nelder_options = {"maxiter": 10000000, "sample_points": 1500}
        if self.svi_options is None:
            self.svi_options = {"iter_svi_MFS": 50000, "step_MFS": 0.000825, "sample_points": 1500}
        if self.params_min is None:
            self.params_min = {"B": 5.0, "C": 1.0, "D": 0.0, "E": -1.0, "S_H": 0.0, "S_V": 0.0}
        if self.params_max is None:
            self.params_max = {"B": 40.0, "C": 3.0, "D": 2.0, "E": 1.0, "S_H": 0.0, "S_V": 0.0}
        if self.params_init is None:
            self.params_init = {"B": 10.0, "C": 1.65, "D": 1.5, "E": -1.0, "S_H": 0.0, "S_V": 0.0}
        if self.fit_flags is None:
            self.fit_flags = {"B": True, "C": True, "D": True, "E": True}


class MagicFormulaGeoExtractor:
    """Extract Magic Formula D parameter using geospatial synchronization.

    This extractor:
    1. Fits Magic Formula tire model (B, C, D, E parameters) from braking wheel dynamics
    2. Extracts D parameter (peak factor) for entire file
    3. Associates D value with measurement wheel GPS trajectory
    4. Matches road patches to trajectory using point-in-polygon testing
    5. Returns D parameter for patches where measurement wheel actually drove over them
    """

    EARTH_RADIUS = 6371000.0  # Earth radius in meters

    def __init__(self, config: Optional[MagicFormulaGeoConfig] = None):
        """Initialize the extractor.

        Args:
            config: Configuration for MF calculation and geospatial sync
        """
        self.config = config or MagicFormulaGeoConfig()
        self._patch_centers = None
        self._patch_timestamps = None
        self._patch_to_frame = None
        self._patch_polygon_start = None  # Polygon start indices
        self._polygon_points = None  # Polygon vertex coordinates
        self._mf_value = None  # Magic Formula D parameter for entire file
        self._mf_params = None  # All Magic Formula parameters (B, C, D, E, S_V, S_H)
        self._mf_std = None  # Standard deviations for MF parameters
        self._mf_positions = None  # Measurement wheel GPS trajectory
        self._mf_timestamps = None
        self._mf_kdtree = None  # Not used anymore, but keeping for potential future use

    def initialize(self, h5_file) -> bool:
        """Initialize extractor by fitting Magic Formula and loading spatial data.

        Args:
            h5_file: Open HDF5 file handle

        Returns:
            True if initialization successful, False otherwise
        """
        logger.info("Initializing Magic Formula geo-extractor...")

        if not self._load_patch_centers(h5_file):
            return False
        if not self._compute_mf_label(h5_file):
            return False

        logger.info("Magic Formula geo-extractor initialized successfully")
        logger.info(f"  Patches: {len(self._patch_centers)}")
        logger.info(f"  MF D parameter: {self._mf_value:.3f}")
        logger.info(f"  Measurement wheel trajectory: {len(self._mf_positions)} GPS positions")
        return True

    def _load_patch_centers(self, h5_file) -> bool:
        """Load and compute patch centers from georeferenced polygons."""
        try:
            # Load polygon data
            polygon_points = h5_file[self.config.polygon_points_key][:]
            start_indices = h5_file[self.config.polygon_start_indices_key][:]

            # Load timestamps
            patch_ts_s = h5_file[self.config.patch_ts_s_key][:]
            patch_ts_ns = h5_file[self.config.patch_ts_ns_key][:]
            frame_timestamps = patch_ts_s.astype(np.float64) + patch_ts_ns.astype(np.float64) * 1e-9

            # Load num patches per frame
            num_patches_per_frame = h5_file[self.config.num_patches_key][:]

            # Compute centers for each patch
            num_patches = len(start_indices)
            num_patches_total = int(num_patches_per_frame.sum())

            # Check for mismatch between datasets
            if num_patches != num_patches_total:
                logger.warning(
                    f"Patch count mismatch: georeferenced={num_patches}, "
                    f"metadata={num_patches_total}. Using minimum."
                )
                # Use the smaller count to avoid index errors
                num_patches = min(num_patches, num_patches_total)

            patch_centers = np.zeros((num_patches, 3), dtype=np.float64)

            for i in range(num_patches):
                start_idx = start_indices[i]
                if i + 1 < len(start_indices):
                    end_idx = start_indices[i + 1]
                else:
                    end_idx = len(polygon_points)

                # Compute centroid of polygon
                patch_points = polygon_points[start_idx:end_idx]
                patch_centers[i] = np.mean(patch_points, axis=0)

            # Build patch to frame mapping
            patch_to_frame = np.zeros(num_patches, dtype=int)
            # Fixed: Include all frames in cumsum (removed [:-1])
            # This creates N+1 indices for N frames: [0, cumsum[0], cumsum[1], ..., total]
            patch_start_indices = np.concatenate([[0], np.cumsum(num_patches_per_frame)])

            # Only iterate over frames that have corresponding timestamps
            num_frames = min(len(num_patches_per_frame), len(frame_timestamps))
            for frame_idx in range(num_frames):
                start_idx = patch_start_indices[frame_idx]
                end_idx = patch_start_indices[frame_idx + 1]  # Safe now: array has N+1 elements
                # Clamp end_idx to num_patches to handle mismatch
                end_idx = min(end_idx, num_patches)
                if start_idx < num_patches:
                    patch_to_frame[start_idx:end_idx] = frame_idx

            # Assign timestamps to patches
            patch_timestamps = frame_timestamps[patch_to_frame]

            self._patch_centers = patch_centers
            self._patch_timestamps = patch_timestamps
            self._patch_to_frame = patch_to_frame

            # Store polygon boundaries for point-in-polygon matching
            self._patch_polygon_start = start_indices
            self._polygon_points = polygon_points

            logger.info(f"Loaded {num_patches} patch centers from georeferenced polygons")
            logger.info(f"  Lat range: [{patch_centers[:, 0].min():.6f}, {patch_centers[:, 0].max():.6f}]")
            logger.info(f"  Lon range: [{patch_centers[:, 1].min():.6f}, {patch_centers[:, 1].max():.6f}]")
            return True

        except KeyError as e:
            logger.error(f"Missing required key in HDF5 file: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to load patch centers: {e}")
            return False

    def _compute_mf_label(self, h5_file) -> bool:
        """Fit Magic Formula and extract D parameter for entire file."""
        try:
            # Load wheel dynamics data
            mw_angular_vel_data = h5_file[self.config.mw_angular_velocity_key]
            vehicle_vel_data = h5_file[self.config.vehicle_velocity_key]
            wheel_fx_data = h5_file[self.config.wheel_force_x_key]
            wheel_fz_data = h5_file[self.config.wheel_force_z_key]
            timestamp_data = h5_file[self.config.mw_timestamp_key]

            # Extract values from structured arrays
            mw_angular_vel = mw_angular_vel_data['value'][:]
            vehicle_vel = vehicle_vel_data['value'][:]
            wheel_fx = wheel_fx_data['value'][:]
            wheel_fz = wheel_fz_data['value'][:]
            timestamps = timestamp_data['value'][:]

            # Load GPS positions
            mw_lat_data = h5_file[self.config.mw_lat_key]
            mw_lon_data = h5_file[self.config.mw_lon_key]
            mw_lat = mw_lat_data['value'][:]
            mw_lon = mw_lon_data['value'][:]

            # Load brake data for filtering (always enabled)
            brake_mask = None
            try:
                brake_data = h5_file[self.config.brake_position_key]
                brake_position = brake_data['value'][:]
                brake_mask = brake_position > self.config.brake_threshold_mm
                logger.info(f"Brake filtering: {brake_mask.sum()} / {len(brake_mask)} samples have brake actuated (>{self.config.brake_threshold_mm}mm)")
            except KeyError:
                logger.warning(f"Brake data key '{self.config.brake_position_key}' not found - skipping brake filtering")
                brake_mask = None

            logger.info(f"Computing Magic Formula D parameter for entire file ({len(mw_angular_vel)} samples)")

            # Compute slip and friction coefficient for all samples
            circumferential_vel = self.config.wheel_radius * mw_angular_vel
            max_velocity = np.maximum(circumferential_vel, vehicle_vel)
            max_velocity = np.where(max_velocity == 0, 1e-6, max_velocity)
            slip = -(circumferential_vel - vehicle_vel) / max_velocity

            wheel_fz_safe = np.where(wheel_fz == 0, 1e-6, wheel_fz)
            friction = -wheel_fx / wheel_fz_safe

            # Filter valid values
            valid_mask = np.isfinite(slip) & np.isfinite(friction)

            # Apply brake filtering
            if brake_mask is not None:
                valid_mask = valid_mask & brake_mask
                logger.info(f"  After brake filtering: {valid_mask.sum()} samples remain")

            slip_valid = slip[valid_mask]
            friction_valid = friction[valid_mask]

            if len(slip_valid) < 100:
                logger.error(f"Insufficient valid data points: {len(slip_valid)}")
                return False

            logger.info(f"  Valid samples: {len(slip_valid)} / {len(slip)}")

            # Fit Magic Formula for entire dataset
            fitting_config = OmegaConf.create({
                "nelder_options": self.config.nelder_options,
                "svi_options": self.config.svi_options,
                "params_min": self.config.params_min,
                "params_max": self.config.params_max,
                "params_init": self.config.params_init,
                "sigma_bound": self.config.sigma_bound,  # Pass configurable sigma bound
            })

            # Extract actual forces (not friction coefficients) for MF fitting
            fx_valid = -wheel_fx[valid_mask]  # Negate to get positive traction force
            fz_valid = wheel_fz[valid_mask]   # Normal load

            # Use our custom fitting function with adaptive sigma bounds
            results = fit_tire_parameters_custom(
                force_n=fx_valid,    # Actual longitudinal force in Newtons
                load_n=fz_valid,     # Actual normal load in Newtons
                sigma=slip_valid,
                config=fitting_config,
                fit_flags=self.config.fit_flags
            )

            params = results["svi"]["parameters"]
            std = results["svi"]["std"]
            d_param = float(params.D)

            # Reject files where MF fitting produces NaN
            if not np.isfinite(d_param):
                logger.error(f"MF fitting produced NaN/Inf D parameter: {d_param}")
                logger.error(f"  This file will be skipped (likely bad sensor data)")
                return False

            # Store all Magic Formula parameters
            self._mf_value = d_param
            self._mf_params = {
                'B': float(params.B),
                'C': float(params.C),
                'D': float(params.D),
                'E': float(params.E),
                'S_V': float(params.S_V),
                'S_H': float(params.S_H),
            }
            self._mf_std = {
                'B_std': float(std.B) if std else None,
                'C_std': float(std.C) if std else None,
                'D_std': float(std.D) if std else None,
                'E_std': float(std.E) if std else None,
            }
            self._mf_positions = np.column_stack([mw_lat, mw_lon, np.zeros_like(mw_lat)])
            self._mf_timestamps = timestamps

            # Build KD-tree for spatial queries
            self._mf_kdtree = cKDTree(self._mf_positions[:, :2])

            logger.info(f"Computed MF parameters: B={params.B:.3f}, C={params.C:.3f}, D={params.D:.3f}, E={params.E:.3f}")
            logger.info(f"  Measurement trajectory: {len(self._mf_positions)} GPS positions")
            return True

        except KeyError as e:
            logger.error(f"Missing required key for MF computation: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to compute MF label: {e}")
            logger.exception(e)
            return False

    @staticmethod
    def lat_lon_distance(lat1, lon1, lat2, lon2):
        """Compute distance in meters between two lat/lon points using Haversine formula."""
        lat1_rad = np.radians(lat1)
        lat2_rad = np.radians(lat2)
        dlat = np.radians(lat2 - lat1)
        dlon = np.radians(lon2 - lon1)

        a = np.sin(dlat / 2.0) ** 2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon / 2.0) ** 2
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

        return MagicFormulaGeoExtractor.EARTH_RADIUS * c

    @staticmethod
    def point_in_polygon(point: np.ndarray, polygon: np.ndarray) -> bool:
        """Test if a point (lat, lon) is inside a polygon using ray casting algorithm.

        Args:
            point: (lat, lon) coordinates
            polygon: (N, 2) array of polygon vertices (lat, lon)

        Returns:
            True if point is inside polygon
        """
        lat, lon = point[0], point[1]
        n = len(polygon)
        inside = False

        p1_lat, p1_lon = polygon[0]
        for i in range(1, n + 1):
            p2_lat, p2_lon = polygon[i % n]

            if lon > min(p1_lon, p2_lon):
                if lon <= max(p1_lon, p2_lon):
                    if lat <= max(p1_lat, p2_lat):
                        if p1_lon != p2_lon:
                            xinters = (lon - p1_lon) * (p2_lat - p1_lat) / (p2_lon - p1_lon) + p1_lat
                        if p1_lat == p2_lat or lat <= xinters:
                            inside = not inside

            p1_lat, p1_lon = p2_lat, p2_lon

        return inside

    def extract_label(self, patch_idx: int) -> Optional[float]:
        """Extract Magic Formula D parameter using point-in-polygon matching.

        Tests if any measurement wheel GPS position is inside the patch polygon.
        This matches the actual workflow: camera sees patch ahead,
        then measurement wheel drives over it.

        Args:
            patch_idx: Index of the patch

        Returns:
            Magic Formula D parameter or None if:
            - patch_idx is out of bounds (road_patches may have more entries than georeferenced)
            - measurement wheel never entered polygon
        """
        # Bounds check - road_patches may have more entries than road_patches_georeferenced
        if patch_idx >= len(self._patch_polygon_start):
            return None

        # Get polygon for this patch
        start_idx = self._patch_polygon_start[patch_idx]
        if patch_idx + 1 < len(self._patch_polygon_start):
            end_idx = self._patch_polygon_start[patch_idx + 1]
        else:
            end_idx = len(self._polygon_points)

        polygon = self._polygon_points[start_idx:end_idx, :2]  # (N, 2) lat/lon

        # Compute bounding box for quick pre-filtering
        min_lat, max_lat = polygon[:, 0].min(), polygon[:, 0].max()
        min_lon, max_lon = polygon[:, 1].min(), polygon[:, 1].max()

        # Check if ANY measurement wheel position is inside this polygon
        for mw_pos in self._mf_positions:
            lat, lon = mw_pos[0], mw_pos[1]

            # Quick bounding box reject
            if not (min_lat <= lat <= max_lat and min_lon <= lon <= max_lon):
                continue

            # Expensive point-in-polygon test
            if self.point_in_polygon(mw_pos[:2], polygon):
                # Match! Measurement wheel drove over this patch
                return self._mf_value

        # Measurement wheel never entered this patch polygon
        return None
