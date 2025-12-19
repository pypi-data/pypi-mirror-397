"""xcat-mesh: NIfTI binary mask -> surface mesh (OBJ) with optional smoothing."""

from .pipeline import run, mesh_from_nifti

__all__ = ["run", "mesh_from_nifti"]
