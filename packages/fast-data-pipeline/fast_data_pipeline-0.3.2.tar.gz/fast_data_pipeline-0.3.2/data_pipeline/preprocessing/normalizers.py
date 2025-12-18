# normalizers.py - Enhanced version

from dataclasses import dataclass
from typing import Dict
import numpy as np
import logging

logger = logging.getLogger(__name__)


@dataclass
class SensorSpec:
    """Sensor specification container."""
    max_range: float
    intensity_bits: int
    reflectivity_bits: int
    signal_bits: int
    max_ring: int
    
    @property
    def intensity_max(self) -> float:
        return 2 ** self.intensity_bits - 1
    
    @property
    def reflectivity_max(self) -> float:
        return 2 ** self.reflectivity_bits - 1
    
    @property
    def signal_max(self) -> float:
        return 2 ** self.signal_bits - 1


class OusterSpecs:
    """Ouster sensor specifications."""
    
    OS1 = SensorSpec(max_range=120.0, intensity_bits=16, reflectivity_bits=8, 
                     signal_bits=16, max_ring=128)
    OS2 = SensorSpec(max_range=240.0, intensity_bits=16, reflectivity_bits=8,
                     signal_bits=16, max_ring=128)
    
    MODELS: Dict[str, SensorSpec] = {
        'OS-1': OS1,
        'OS-2': OS2
    }


class OusterLidarNormalizer:
    """
    Normalizer for Ouster LiDAR data based on sensor specifications.
    
    Feature order: [x, y, z, intensity, timestamp, reflectivity, ring, 
                    ambient, range, signal, near_ir]
    """
    
    FEATURE_NAMES = ['x', 'y', 'z', 'intensity', 'reflectivity', 
                     'ring', 'ambient', 'range']
    NUM_FEATURES = 8
    
    def __init__(self, sensor_model: str = "OS-2", max_range: float = None):
        """
        Initialize normalizer with sensor specifications.
        
        Args:
            sensor_model: Sensor model name
            max_range: Override maximum range if provided
            
        Raises:
            ValueError: If sensor model is unknown
        """
        if sensor_model not in OusterSpecs.MODELS:
            available = ', '.join(OusterSpecs.MODELS.keys())
            raise ValueError(f"Unknown sensor model '{sensor_model}'. Available: {available}")
        
        self.spec = OusterSpecs.MODELS[sensor_model]
        if max_range is not None:
            self.spec.max_range = max_range
        
        self._setup_normalization_params()
        self._log_initialization()
    
    def _setup_normalization_params(self):
        """Setup normalization parameter arrays."""
        r = self.spec.max_range
        
    def _setup_normalization_params(self):
        r = self.spec.max_range
        
        self.feature_min = np.array([
            -r, -r, -r,                    # xyz (3)
            0.0,                           # intensity (1)
            0.0,                           # reflectivity (1)
            0.0,                           # ring (1)
            0.0,                           # ambient (1)
            0.0                            # range (1)
        ], dtype=np.float32)  # Total: 8
        
        self.feature_max = np.array([
            r, r, r,                       # xyz (3)
            self.spec.intensity_max,       # intensity (1)
            self.spec.reflectivity_max,    # reflectivity (1)
            self.spec.max_ring,            # ring (1)
            self.spec.signal_max,          # ambient (1)
            r                              # range (1)
        ], dtype=np.float32)
        
        self.feature_range = self.feature_max - self.feature_min
    
    def _log_initialization(self):
        """Log initialization details."""
        logger.info(f"Ouster LiDAR normalizer initialized:")
        logger.info(f"  Sensor: {self.spec}")
        logger.info(f"  Features: {len(self.FEATURE_NAMES)}")
    
    def normalize(self, lidar_pts: np.ndarray) -> np.ndarray:
        """
        Normalize lidar points to [0, 1] range.
        
        Args:
            lidar_pts: Lidar features in original scale (N, 11)
            
        Returns:
            Normalized features in [0, 1] range
            
        Raises:
            ValueError: If feature count mismatch
        """
        self._validate_shape(lidar_pts)
        # Add epsilon to avoid division by zero
        return (lidar_pts - self.feature_min) / (self.feature_range + 1e-8)
    
    def denormalize(self, normalized_pts: np.ndarray) -> np.ndarray:
        """
        Denormalize points from [0, 1] to original range.
        
        Args:
            normalized_pts: Normalized features (N, 11)
            
        Returns:
            Original scale features
            
        Raises:
            ValueError: If feature count mismatch
        """
        self._validate_shape(normalized_pts)
        return normalized_pts * self.feature_range + self.feature_min
    
    def _validate_shape(self, pts: np.ndarray):
        """Validate point array shape."""
        if pts.shape[1] != self.NUM_FEATURES:
            raise ValueError(f"Expected {self.NUM_FEATURES} features, got {pts.shape[1]}")
    
    def get_feature_info(self) -> Dict:
        """
        Get feature normalization information.
        
        Returns:
            Dictionary with feature metadata
        """
        return {
            'feature_names': self.FEATURE_NAMES,
            'feature_min': self.feature_min.tolist(),
            'feature_max': self.feature_max.tolist(),
            'feature_range': self.feature_range.tolist(),
            'sensor_spec': self.spec.__dict__
        }
    
class RGBNormalizer:
    """
    Normalizer for RGB images.
    Converts uint8 images to float32 in [0, 1] range.
    """
    
    def __init__(self, mean: np.ndarray = None, std: np.ndarray = None):
        """
        Initialize RGB normalizer.
        
        Args:
            mean: Channel means for normalization (optional)
            std: Channel standard deviations for normalization (optional)
        """
        self.mean = mean
        self.std = std
        
        if mean is not None and std is not None:
            logger.info(f"RGB normalizer initialized with mean={mean}, std={std}")
        else:
            logger.info("RGB normalizer initialized for [0, 1] scaling")
    
    def normalize(self, rgb_img: np.ndarray) -> np.ndarray:
        """
        Normalize RGB image to [0, 1] range.
        
        Args:
            rgb_img: RGB image as uint8 (H, W, 3)
            
        Returns:
            Normalized image as float32
        """
        img_float = rgb_img.astype(np.float32) / 255.0
        
        if self.mean is not None and self.std is not None:
            img_float = (img_float - self.mean) / self.std
        
        return img_float
    
    def denormalize(self, normalized_img: np.ndarray) -> np.ndarray:
        """
        Denormalize image back to [0, 255] uint8 range.
        
        Args:
            normalized_img: Normalized image (H, W, 3)
            
        Returns:
            Original scale image as uint8
        """
        if self.mean is not None and self.std is not None:
            normalized_img = normalized_img * self.std + self.mean
        
        img_uint8 = (normalized_img * 255.0).clip(0, 255).astype(np.uint8)
        return img_uint8