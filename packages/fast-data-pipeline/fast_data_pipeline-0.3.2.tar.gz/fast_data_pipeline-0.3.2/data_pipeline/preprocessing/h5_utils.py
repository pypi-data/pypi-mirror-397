"""
HDF5 utilities for handling raw data files.
Used by preprocessing and legacy datasets.
"""
import numpy as np
from pathlib import Path
import logging
from typing import Any, Dict, Tuple, List
import h5py

logger = logging.getLogger(__name__)


def safe_h5_index(dataset, idx: int):
    """
    Safely index h5py dataset with multiple fallback strategies.
    
    Handles various HDF5 edge cases:
    - Inconsistent return types (scalar vs array)
    - Type conversion issues
    - Chunking complications
    
    Args:
        dataset: h5py Dataset object
        idx: Index to access
    
    Returns:
        Data at index as numpy array
    """
    idx = int(idx)
    
    # Strategy 1: Direct indexing
    try:
        data = dataset[idx]
        return np.asarray(data)
    except (TypeError, ValueError) as e:
        logger.debug(f"Direct indexing failed: {e}")
    
    # Strategy 2: Fancy indexing
    try:
        data = dataset[[idx]]
        return np.asarray(data[0])
    except (TypeError, ValueError) as e:
        logger.debug(f"Fancy indexing failed: {e}")
    
    # Strategy 3: Slice indexing
    try:
        data = dataset[idx:idx+1]
        return np.asarray(data[0])
    except (TypeError, ValueError) as e:
        logger.debug(f"Slice indexing failed: {e}")
    
    # Strategy 4: Fallback - load entire dataset (slow!)
    try:
        logger.warning(f"Using fallback: reading entire dataset")
        all_data = dataset[:]
        return np.asarray(all_data[idx])
    except Exception as e:
        logger.error(f"All indexing strategies failed: {e}")
        raise


def validate_h5_preprocessing_structure(h5_file, required_keys: Dict[str, str]) -> Tuple[bool, List[str]]:
    """
    Validate HDF5 file has required structure for preprocessing.
    
    Args:
        h5_file: Open h5py File object
        required_keys: Dict of {key_name: key_path} to check
    
    Returns:
        Tuple of (is_valid, list_of_missing_keys)
    """
    missing_keys = []
    
    for key_name, key_path in required_keys.items():
        try:
            if key_path not in h5_file:
                missing_keys.append(f"{key_name} ({key_path})")
        except Exception as e:
            missing_keys.append(f"{key_name} ({key_path}) - Error: {e}")
    
    return len(missing_keys) == 0, missing_keys


def get_h5_file_info(h5_path: Path) -> Dict[str, Any]:
    """
    Get basic info about HDF5 file structure.
    
    Args:
        h5_path: Path to HDF5 file
    
    Returns:
        Dict with file info
    """
    info = {
        'path': str(h5_path),
        'size_mb': h5_path.stat().st_size / (1024 * 1024),
        'valid': False,
        'error': None,
        'keys': []
    }
    
    try:
        with h5py.File(h5_path, 'r') as f:
            info['keys'] = list(f.keys())
            info['valid'] = True
    except Exception as e:
        info['error'] = str(e)
    
    return info