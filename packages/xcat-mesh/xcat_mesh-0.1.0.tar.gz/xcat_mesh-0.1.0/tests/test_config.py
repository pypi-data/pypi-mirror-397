import json
import tempfile
from xcat_mesh.config import load_config
from xcat_mesh.errors import ConfigError

def test_config_requires_output():
    cfg = {
        "target_resolution_mm": [1,1,1],
        "reorient_canonical": True,
        "smooth": {"enabled": True, "num_iter": 10, "weight": 0.1, "device": "cpu"},
        "output": {}
    }
    with tempfile.NamedTemporaryFile("w+", suffix=".json") as f:
        json.dump(cfg, f)
        f.flush()
        try:
            load_config(f.name)
            assert False, "expected ConfigError"
        except ConfigError:
            pass
