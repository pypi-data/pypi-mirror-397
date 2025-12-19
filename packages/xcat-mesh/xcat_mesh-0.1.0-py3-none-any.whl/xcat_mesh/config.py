from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
import json

from .errors import ConfigError

@dataclass(frozen=True)
class SmoothConfig:
    enabled: bool = True
    method: str = "laplacian"   # "laplacian" | "taubin" | "none"
    num_iter: int = 10
    weight: float = 0.1         # laplacian
    lambda_: float = 0.5        # taubin
    mu: float = -0.53           # taubin
    device: str = "cpu"

@dataclass(frozen=True)
class OutputConfig:
    mesh_unsmoothed_path: Optional[str] = None
    mesh_smoothed_path: Optional[str] = None

@dataclass(frozen=True)
class MeshConfig:
    target_resolution_mm: Optional[Tuple[float, float, float]] = (1.0, 1.0, 1.0)
    reorient_canonical: bool = True
    smooth: SmoothConfig = SmoothConfig()
    output: OutputConfig = OutputConfig()

def load_config(path: str | Path) -> MeshConfig:
    p = Path(path)
    if not p.exists():
        raise ConfigError(f"Config file not found: {p}")

    data = json.loads(p.read_text())

    # target_resolution_mm can be null to disable resampling
    tr = data.get("target_resolution_mm", (1.0, 1.0, 1.0))
    if tr is not None:
        if (not isinstance(tr, (list, tuple))) or len(tr) != 3:
            raise ConfigError("target_resolution_mm must be a 3-element list/tuple or null.")
        tr = tuple(float(x) for x in tr)

    reorient = bool(data.get("reorient_canonical", True))

    s = data.get("smooth", {}) or {}
    smooth = SmoothConfig(
        enabled=bool(s.get("enabled", True)),
        method=str(s.get("method", "laplacian")).lower(),
        num_iter=int(s.get("num_iter", 10)),
        weight=float(s.get("weight", 0.1)),
        lambda_=float(s.get("lambda", 0.5)),
        mu=float(s.get("mu", -0.53)),
        device=str(s.get("device", "cpu")),
    )

    if smooth.method not in {"laplacian", "taubin", "none"}:
        raise ConfigError("smooth.method must be one of: laplacian, taubin, none")


    o = data.get("output", {}) or {}
    output = OutputConfig(
        mesh_unsmoothed_path=o.get("mesh_unsmoothed_path"),
        mesh_smoothed_path=o.get("mesh_smoothed_path"),
    )

    if not (output.mesh_unsmoothed_path or output.mesh_smoothed_path):
        raise ConfigError(
            "Config.output must specify at least one of mesh_unsmoothed_path or mesh_smoothed_path."
        )

    if smooth.num_iter < 0:
        raise ConfigError("smooth.num_iter must be >= 0")
    if not (0.0 <= smooth.weight <= 1.0):
        raise ConfigError("smooth.weight should be in [0, 1] (recommended).")

    return MeshConfig(
        target_resolution_mm=tr,
        reorient_canonical=reorient,
        smooth=smooth,
        output=output,
    )

def default_config_dict() -> Dict[str, Any]:
    return {
        "target_resolution_mm": [1.0, 1.0, 1.0],
        "reorient_canonical": True,
        "smooth": {
            "enabled": True,
            "method": "laplacian",
            "num_iter": 10,
            "weight": 0.1,
            "lambda": 0.5,
            "mu": -0.53,
            "device": "cpu"
        },
        "output": {
            "mesh_unsmoothed_path": "mesh_raw.obj",
            "mesh_smoothed_path": "mesh_smooth.obj"
        },
    }
