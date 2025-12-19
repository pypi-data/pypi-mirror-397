from __future__ import annotations
from pathlib import Path
from typing import Optional, Tuple, Dict, Any

import numpy as np
from tqdm import tqdm

from .config import load_config, MeshConfig
from .io import load_nifti_mask, save_obj
from .validate import assert_binary_mask, assert_non_empty
from .resample import resample_to_target_resolution
from .mesh import marching_cubes_binary
from .smooth import smooth_vertices

def mesh_from_nifti(nifti_path: str | Path, cfg: MeshConfig):
    """
    Convert a NIfTI binary mask to a surface mesh.

    Args:
        nifti_path: Path to input NIfTI file
        cfg: Mesh configuration

    Returns:
        Tuple of (vertices, faces, smoothed_vertices)
    """
    with tqdm(total=5, desc="Mesh generation", unit="step") as pbar:
        pbar.set_description("Loading NIfTI mask")
        mask, spacing = load_nifti_mask(nifti_path, reorient_canonical=cfg.reorient_canonical)
        pbar.update(1)

        pbar.set_description("Validating mask")
        assert_binary_mask(mask)
        assert_non_empty(mask)
        pbar.update(1)

        if cfg.target_resolution_mm is not None:
            pbar.set_description("Resampling to target resolution")
            mask, spacing = resample_to_target_resolution(mask, spacing, cfg.target_resolution_mm)
        pbar.update(1)

        # Marching cubes expects numeric array; ensure 0/1
        mask01 = (mask == 1).astype(np.uint8)

        pbar.set_description("Running marching cubes")
        verts, faces = marching_cubes_binary(mask01, spacing)
        pbar.update(1)

        smoothed = None
        if cfg.smooth.enabled and cfg.smooth.num_iter > 0 and cfg.smooth.weight > 0.0:
            pbar.set_description(f"Smoothing ({cfg.smooth.method}, {cfg.smooth.num_iter} iter)")
            smoothed = smooth_vertices(
                verts, faces,
                method=cfg.smooth.method,
                num_iter=cfg.smooth.num_iter,
                weight=cfg.smooth.weight,
                lambda_=cfg.smooth.lambda_,
                mu=cfg.smooth.mu,
                device=cfg.smooth.device,
            )
        pbar.update(1)

    return verts, faces, smoothed

def run(nifti_path: str | Path, config_path: str | Path) -> None:
    """
    Main pipeline: load NIfTI mask, generate mesh, and save output.

    Args:
        nifti_path: Path to input NIfTI file
        config_path: Path to config JSON file
    """
    cfg = load_config(config_path)
    verts, faces, smoothed = mesh_from_nifti(nifti_path, cfg)

    print(f"Generated mesh: {len(verts)} vertices, {len(faces)} faces")

    if cfg.output.mesh_unsmoothed_path:
        print(f"Saving unsmoothed mesh to: {cfg.output.mesh_unsmoothed_path}")
        save_obj(cfg.output.mesh_unsmoothed_path, verts, faces)

    if cfg.output.mesh_smoothed_path:
        if smoothed is None:
            # If smoothing disabled but user asked for smoothed output, fall back to raw
            print(f"Saving mesh to: {cfg.output.mesh_smoothed_path}")
            save_obj(cfg.output.mesh_smoothed_path, verts, faces)
        else:
            print(f"Saving smoothed mesh to: {cfg.output.mesh_smoothed_path}")
            save_obj(cfg.output.mesh_smoothed_path, smoothed, faces)
