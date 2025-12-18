"""Configuration classes for preprocessing pipelines."""
from dataclasses import dataclass
from typing import Tuple
from pathlib import Path


@dataclass
class DatasetKeys:
    """HDF5 dataset keys configuration."""
    patch_table: str = 'hi5/road/road_patches/pointcloud_data'
    patch_num: str = 'hi5/road/road_patches/num_patches'
    patch_list_ts: str = 'hi5/road/road_patches/timestamp_s'
    cam_ts: str = 'hi5/perception/synchronized/camera/timestamp_s'
    cam_img: str = 'hi5/perception/synchronized/camera/data'
    lidar_table: str = 'hi5/perception/synchronized/lidar/data/all_points'
    lidar_frame_idx: str = 'hi5/perception/synchronized/lidar/data/frame_start_indices'
    label: str = "rfmu/marwis/data/friction"


@dataclass
class PreprocessConfig:
    """Base configuration for all preprocessing pipelines."""
    # I/O
    source_folder: str
    dest_folder: str
    source_pattern: str = "*.h5"
    output_suffix: str = "_preprocessed"
    skip_existing: bool = True
    
    # Image config
    image_full_size: Tuple[int, int] = (3032, 5032)
    
    # Dataset keys
    keys: DatasetKeys = None
    
    # Model config
    sensor_model: str = "OS-2"
    max_lidar_range: float = 240.0
    lidar_feature_dim: int = 11
    rgb_feature_dim: int = 3
    
    # Processing config
    batch_size: int = 32
    max_cache_size: int = 20
    
    def __post_init__(self):
        if self.keys is None:
            self.keys = DatasetKeys()
    
    @property
    def total_feature_dim(self) -> int:
        return self.lidar_feature_dim + self.rgb_feature_dim


@dataclass
class PointCloudPreprocessConfig(PreprocessConfig):
    """Configuration for PointNet-style preprocessing (3D points with RGB)."""
    min_points: int = 100
    output_suffix: str = "_pointcloud_preprocessed"


@dataclass
class SparseImagePreprocessConfig(PreprocessConfig):
    """Configuration for sparse image preprocessing (2D projected sparse grid)."""
    output_image_size: Tuple[int, int] = (224, 224)
    max_points_per_pixel: int = 5
    output_suffix: str = "_sparse_preprocessed"