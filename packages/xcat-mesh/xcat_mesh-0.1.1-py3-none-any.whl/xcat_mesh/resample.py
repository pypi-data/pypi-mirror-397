from __future__ import annotations
from typing import Tuple
import numpy as np
from scipy.ndimage import zoom

def resample_to_target_resolution(
    mask: np.ndarray,
    spacing_mm: Tuple[float, float, float],
    target_mm: Tuple[float, float, float],
) -> Tuple[np.ndarray, Tuple[float, float, float]]:
    """
    Nearest-neighbor resample a label mask to target voxel spacing.

    Args:
        mask: Input 3D mask array
        spacing_mm: Current voxel spacing (x, y, z) in millimeters
        target_mm: Target voxel spacing (x, y, z) in millimeters

    Returns:
        Tuple of (resampled mask, target spacing)

    Note:
        Uses order=0 (nearest neighbor) interpolation to preserve label values
    """
    sx, sy, sz = spacing_mm
    tx, ty, tz = target_mm

    # zoom factor = old_spacing / new_spacing
    factors = (sx / tx, sy / ty, sz / tz)

    # Nearest neighbor to preserve labels
    out = zoom(mask, zoom=factors, order=0)
    out = out.astype(mask.dtype, copy=False)
    return out, target_mm
