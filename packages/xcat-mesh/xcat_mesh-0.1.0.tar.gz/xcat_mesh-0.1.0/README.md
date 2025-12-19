# xcat-mesh

Fast and efficient conversion of **binary NIfTI segmentation masks** (`.nii` / `.nii.gz`) into high-quality 3D surface meshes.

## Features

- **🚀 Fast**: Optimized pipeline with progress tracking
- **🎯 Simple**: Single command to generate meshes
- **🔧 Configurable**: JSON-based configuration for all parameters
- **💻 GPU Accelerated**: Optional GPU smoothing with PyTorch
- **📦 Lightweight**: Minimal dependencies, clean codebase
- **🔄 Flexible**: Supports resampling, reorientation, and multiple smoothing methods

## What It Does

`xcat-mesh` converts 3D medical imaging segmentation masks into polygon surface meshes using:

1. **Marching Cubes Algorithm**: Extracts isosurface at level 0.5
2. **Optional Resampling**: Resample to target voxel spacing
3. **Mesh Smoothing**: Laplacian or Taubin smoothing (CPU/GPU)
4. **OBJ Export**: Standard Wavefront OBJ format

Perfect for visualizing anatomical structures, 3D printing medical models, or preparing meshes for computational simulations.

### About XCAT 3.0

This tool was developed as part of research in generating **XCAT 3.0 Digital Twins** - a comprehensive library of personalized computational phantoms derived from CT scans. XCAT 3.0 enables researchers to create patient-specific anatomical models for:

- Medical imaging simulation and validation
- Radiation dose optimization
- Image reconstruction algorithm development
- AI/ML training with ground truth anatomies
- Virtual clinical trials

The mesh generation pipeline in `xcat-mesh` is a key component for converting segmented anatomical structures into high-quality surface representations used in the XCAT phantom library.

---

## Installation

### Basic Installation (CPU only)

```bash
pip install xcat-mesh
```

### GPU-Accelerated Smoothing

```bash
pip install "xcat-mesh[gpu]"
```

This installs PyTorch for GPU-accelerated mesh smoothing.

### Development Installation

```bash
git clone https://github.com/yourusername/xcat-mesh.git
cd xcat-mesh
pip install -e .
```

---

## Quick Start

### CLI Usage

**Step 1: Create a default configuration file**

```bash
xcat-mesh init-config --out config.json
```

**Step 2: Run the meshing pipeline**

```bash
xcat-mesh run --input segmentation_mask.nii.gz --config config.json
```

That's it! Your meshes will be saved to the paths specified in `config.json`.

### One-Liner

```bash
xcat-mesh init-config --out config.json && xcat-mesh run --input mask.nii.gz --config config.json
```

---

## Configuration

The generated `config.json` looks like this:

```json
{
  "target_resolution_mm": [1.0, 1.0, 1.0],
  "reorient_canonical": true,
  "smooth": {
    "enabled": true,
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
  }
}
```

### Configuration Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `target_resolution_mm` | `[float, float, float]` or `null` | `[1.0, 1.0, 1.0]` | Target voxel spacing in mm (x,y,z). Set to `null` to disable resampling. |
| `reorient_canonical` | `bool` | `true` | Reorient image to RAS+ canonical orientation before processing. |
| **smooth.enabled** | `bool` | `true` | Enable mesh smoothing. |
| **smooth.method** | `str` | `"laplacian"` | Smoothing method: `"laplacian"`, `"taubin"`, or `"none"`. |
| **smooth.num_iter** | `int` | `10` | Number of smoothing iterations. |
| **smooth.weight** | `float` | `0.1` | Smoothing weight for Laplacian method (0-1). Higher = more smoothing. |
| **smooth.lambda** | `float` | `0.5` | Shrinkage parameter for Taubin smoothing. |
| **smooth.mu** | `float` | `-0.53` | Inflation parameter for Taubin smoothing (typically negative). |
| **smooth.device** | `str` | `"cpu"` | PyTorch device: `"cpu"`, `"cuda"`, or `"cuda:0"`, etc. |
| **output.mesh_unsmoothed_path** | `str` or `null` | `"mesh_raw.obj"` | Output path for raw mesh. |
| **output.mesh_smoothed_path** | `str` or `null` | `"mesh_smooth.obj"` | Output path for smoothed mesh. |

**Note**: At least one output path must be specified.

---

## Python API

### Basic Usage

```python
from xcat_mesh import run

run("segmentation_mask.nii.gz", "config.json")
```

### Advanced Usage

```python
from xcat_mesh import mesh_from_nifti
from xcat_mesh.config import load_config
from xcat_mesh.io import save_obj

# Load configuration
config = load_config("config.json")

# Generate mesh
verts, faces, smoothed_verts = mesh_from_nifti("mask.nii.gz", config)

# Save outputs
save_obj("output_raw.obj", verts, faces)
if smoothed_verts is not None:
    save_obj("output_smooth.obj", smoothed_verts, faces)

print(f"Generated {len(verts)} vertices, {len(faces)} faces")
```

---

## Smoothing Methods

### Laplacian Smoothing

Classic mesh smoothing that moves each vertex toward the average of its neighbors.

```
v_new = v_old + weight × (mean(neighbors) - v_old)
```

- **Pros**: Simple, fast, effective
- **Cons**: Can shrink the mesh over many iterations
- **Recommended**: `weight=0.1`, `num_iter=10-50`

### Taubin Smoothing

Two-step smoothing that reduces shrinkage by alternating between shrinkage and inflation.

```
Step 1: v = v + lambda × L(v)   (shrink)
Step 2: v = v + mu × L(v)       (inflate, mu < 0)
```

- **Pros**: Minimal volume loss, better shape preservation
- **Cons**: Slightly slower (2x iterations)
- **Recommended**: `lambda=0.5`, `mu=-0.53`, `num_iter=10-20`

---

## Examples

### Example 1: High-Quality Mesh with GPU Smoothing

```json
{
  "target_resolution_mm": [0.5, 0.5, 0.5],
  "reorient_canonical": true,
  "smooth": {
    "enabled": true,
    "method": "taubin",
    "num_iter": 20,
    "lambda": 0.5,
    "mu": -0.53,
    "device": "cuda:0"
  },
  "output": {
    "mesh_smoothed_path": "high_quality_mesh.obj"
  }
}
```

### Example 2: Raw Mesh Only (No Smoothing)

```json
{
  "target_resolution_mm": null,
  "reorient_canonical": false,
  "smooth": {
    "enabled": false
  },
  "output": {
    "mesh_unsmoothed_path": "raw_mesh.obj"
  }
}
```

### Example 3: Heavy Smoothing for Visualization

```json
{
  "target_resolution_mm": [1.0, 1.0, 1.0],
  "smooth": {
    "enabled": true,
    "method": "laplacian",
    "num_iter": 100,
    "weight": 0.2,
    "device": "cpu"
  },
  "output": {
    "mesh_smoothed_path": "smooth_for_viz.obj"
  }
}
```

---

## Requirements

- Python 3.9+
- NumPy >= 1.22
- NiBabel >= 5.0
- scikit-image >= 0.20
- SciPy >= 1.9
- tqdm >= 4.65
- PyTorch >= 2.0 (optional, for GPU smoothing)

---

## Input Requirements

- **Format**: NIfTI (`.nii` or `.nii.gz`)
- **Values**: Binary mask with values `{0, 1}` where:
  - `0` = background
  - `1` = foreground (structure to mesh)
- **Dimensions**: 3D volume (e.g., 256×256×128)

---

## Output Format

Standard Wavefront OBJ format with:
- Vertex coordinates (`v x y z`)
- Triangle faces (`f v1 v2 v3`, 1-indexed)

Compatible with:
- Blender, MeshLab, Rhino
- Unity, Unreal Engine
- MATLAB, Python (trimesh, pyvista)

---

## Performance Tips

1. **Use GPU for large meshes**: Set `"device": "cuda:0"` if you have PyTorch with CUDA
2. **Resample before meshing**: Lower resolution = faster processing
3. **Adjust smoothing iterations**: Start with 10, increase if needed
4. **Disable smoothing for speed**: Set `"enabled": false` for instant meshing

---

## Troubleshooting

### Issue: "Smoothing requires PyTorch"

**Solution**: Install PyTorch or disable smoothing:
```bash
pip install torch  # CPU version
# OR
pip install "xcat-mesh[gpu]"  # GPU version
```

### Issue: Mesh looks blocky

**Solution**: Increase smoothing iterations or weight:
```json
"smooth": {
  "num_iter": 50,
  "weight": 0.15
}
```

### Issue: Mesh shrinks too much

**Solution**: Use Taubin smoothing or reduce weight:
```json
"smooth": {
  "method": "taubin",
  "num_iter": 20
}
```

### Issue: Out of memory

**Solution**: Resample to lower resolution first:
```json
"target_resolution_mm": [2.0, 2.0, 2.0]
```

---

## License

Apache 2.0 License - see [LICENSE](LICENSE) file for details.

---

## Contributing

Contributions welcome! Please open an issue or submit a pull request.

---

## Citation

If you use this tool in your research, **please cite the XCAT 3.0 paper**:

```bibtex
@article{dahal2025xcat,
  title={XCAT 3.0: A comprehensive library of personalized digital twins derived from CT scans},
  author={Dahal, Lavsen and Ghojoghnejad, Mobina and Vancoillie, Liesbeth and Ghosh, Dhrubajyoti and Bhandari, Yubraj and Kim, David and Ho, Fong Chi and Tushar, Fakrul Islam and Luo, Sheng and Lafata, Kyle J and others},
  journal={Medical Image Analysis},
  pages={103636},
  year={2025},
  publisher={Elsevier}
}
```

**Reference**: Dahal, L., et al. (2025). XCAT 3.0: A comprehensive library of personalized digital twins derived from CT scans. *Medical Image Analysis*, 103636.

---

## Acknowledgments

- Uses [scikit-image](https://scikit-image.org/) for marching cubes algorithm
- Uses [NiBabel](https://nipy.org/nibabel/) for NIfTI file I/O
- Smoothing algorithms based on classic mesh processing literature
