from __future__ import annotations
import argparse
import json
from pathlib import Path

from .pipeline import run
from .config import default_config_dict

def _cmd_init_config(args: argparse.Namespace) -> int:
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(default_config_dict(), indent=2) + "\n")
    print(f"Wrote default config to: {out}")
    return 0

def _cmd_run(args: argparse.Namespace) -> int:
    run(args.input, args.config)
    print("Done.")
    return 0

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="xcat-mesh", description="Binary NIfTI mask -> surface mesh (OBJ)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init-config", help="Write a default config.json template")
    p_init.add_argument("--out", required=True, help="Output path for config.json")
    p_init.set_defaults(func=_cmd_init_config)

    p_run = sub.add_parser("run", help="Run meshing pipeline")
    p_run.add_argument("--input", required=True, help="Path to binary NIfTI mask (.nii/.nii.gz)")
    p_run.add_argument("--config", required=True, help="Path to config.json")
    p_run.set_defaults(func=_cmd_run)

    args = parser.parse_args(argv)
    return args.func(args)
