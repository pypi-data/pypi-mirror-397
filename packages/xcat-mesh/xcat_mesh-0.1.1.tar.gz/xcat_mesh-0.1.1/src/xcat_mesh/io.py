from __future__ import annotations
from pathlib import Path
from typing import Tuple
import numpy as np
import nibabel as nib

def load_nifti_mask(path: str | Path, reorient_canonical: bool = True) -> Tuple[np.ndarray, Tuple[float, float, float]]:
    """
    Load NIfTI mask and return (mask_array, voxel_spacing_mm).

    Args:
        path: Path to NIfTI file (.nii or .nii.gz)
        reorient_canonical: If True, reorient to RAS+ canonical orientation

    Returns:
        Tuple of (mask array, voxel spacing in mm)
    """
    img = nib.load(str(path))
    if reorient_canonical:
        img = nib.as_closest_canonical(img)

    data = img.get_fdata()  # float64

    # Convert to compact integer type (validation happens later in pipeline)
    mask = data.astype(np.uint8)

    zooms = img.header.get_zooms()
    # Handle both 3D and 4D NIfTI (take first 3 spatial dimensions)
    spacing = (float(zooms[0]), float(zooms[1]), float(zooms[2]))
    return mask, spacing

def save_obj(path: str | Path, verts: np.ndarray, faces: np.ndarray) -> None:
    """
    Save mesh as Wavefront OBJ file.

    Args:
        path: Output path for .obj file
        verts: Vertex coordinates (N, 3)
        faces: Triangle face indices (M, 3)
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)

    with p.open("w") as f:
        # Write vertices efficiently using vectorized string formatting
        vertex_lines = '\n'.join(f'v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}' for v in verts)
        f.write(vertex_lines)
        f.write('\n')

        # OBJ uses 1-based indexing
        face_lines = '\n'.join(f'f {int(tri[0])+1} {int(tri[1])+1} {int(tri[2])+1}' for tri in faces)
        f.write(face_lines)
        f.write('\n')
