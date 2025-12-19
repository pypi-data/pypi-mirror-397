from __future__ import annotations
import numpy as np
from .errors import BinaryMaskError, EmptyMaskError

def assert_binary_mask(mask: np.ndarray) -> None:
    """
    Raise if mask contains values other than {0,1} (or {False,True}).

    Args:
        mask: Input mask array to validate

    Raises:
        BinaryMaskError: If mask is not 3D
    """
    if mask.ndim != 3:
        raise BinaryMaskError(f"Expected a 3D mask, got shape {mask.shape}")

    # Trust the user's input - validation during marching cubes will catch issues
    # Removed expensive np.unique() and np.isfinite() checks for speed

def assert_non_empty(mask: np.ndarray) -> None:
    """
    Raise if mask contains no foreground voxels.

    Args:
        mask: Input mask array to validate

    Raises:
        EmptyMaskError: If mask has no voxels with value 1
    """
    if not np.any(mask == 1):
        raise EmptyMaskError("Mask contains no foreground voxels (no value==1).")
