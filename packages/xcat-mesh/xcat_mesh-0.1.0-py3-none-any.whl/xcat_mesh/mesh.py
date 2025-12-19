from __future__ import annotations
from typing import Tuple
import numpy as np
from skimage import measure

def marching_cubes_binary(mask: np.ndarray, spacing_mm: Tuple[float, float, float]) -> Tuple[np.ndarray, np.ndarray]:
    """
    Run marching cubes on a binary mask (values 0/1) and return (verts, faces).

    Args:
        mask: Binary 3D mask array with values {0, 1}
        spacing_mm: Voxel spacing (x, y, z) in millimeters

    Returns:
        Tuple of (vertices, faces) where vertices are (N, 3) float32 coordinates
        and faces are (M, 3) int32 triangle indices

    Note:
        Uses level=0.5 to extract the isosurface between 0 and 1
    """
    # Use level=0.5 so the surface is between 0 and 1
    verts, faces, _normals, _values = measure.marching_cubes(mask, level=0.5, spacing=spacing_mm)
    return verts.astype(np.float32, copy=False), faces.astype(np.int32, copy=False)
