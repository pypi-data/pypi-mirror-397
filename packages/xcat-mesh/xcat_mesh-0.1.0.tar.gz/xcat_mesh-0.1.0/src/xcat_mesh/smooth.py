from __future__ import annotations
import numpy as np

def _build_adjacency_torch(faces_t, num_verts: int, device: str):
    """
    Build sparse adjacency matrix from triangle faces.

    Args:
        faces_t: Torch tensor of face indices (M, 3)
        num_verts: Total number of vertices
        device: Torch device string

    Returns:
        Tuple of (adjacency matrix, row sums) for Laplacian smoothing
    """
    import torch

    # Extract edges from triangular faces: (v0,v1), (v1,v2), (v0,v2)
    edges = torch.cat([faces_t[:, :2], faces_t[:, 1:], faces_t[:, [0, 2]]], dim=0)
    # Make undirected by adding reverse edges
    edges = torch.cat([edges, edges[:, [1, 0]]], dim=0)
    edges = torch.unique(edges, dim=0)

    edge_weights = torch.ones(edges.shape[0], device=device)

    # Build sparse adjacency matrix (edges are already bidirectional)
    A = torch.sparse_coo_tensor(edges.t(), edge_weights, torch.Size([num_verts, num_verts]))
    # Add small epsilon to prevent division by zero for isolated vertices
    row_sum = torch.sparse.sum(A, dim=1).to_dense().clamp(min=1e-8)
    return A, row_sum

def _laplacian_step_torch(v, A, row_sum):
    """
    Compute one Laplacian smoothing step: L(v) = mean(neighbors) - v.

    Args:
        v: Vertex positions (N, 3)
        A: Sparse adjacency matrix
        row_sum: Row sums of adjacency matrix for normalization

    Returns:
        Laplacian displacement vectors
    """
    import torch
    mean = torch.sparse.mm(A, v)
    mean = mean / row_sum.unsqueeze(-1)
    return mean - v

def smooth_vertices(
    verts: np.ndarray,
    faces: np.ndarray,
    method: str = "laplacian",
    num_iter: int = 10,
    weight: float = 0.1,      # laplacian
    lambda_: float = 0.5,     # taubin
    mu: float = -0.53,        # taubin
    device: str = "cuda:0",
) -> np.ndarray:
    """
    Apply mesh smoothing to vertices using PyTorch.

    Args:
        verts: Vertex positions (N, 3) as numpy array
        faces: Triangle face indices (M, 3) as numpy array
        method: Smoothing method - "laplacian", "taubin", or "none"
        num_iter: Number of smoothing iterations
        weight: Smoothing weight for Laplacian method (0-1)
        lambda_: Shrinkage factor for Taubin method
        mu: Inflation factor for Taubin method (typically negative)
        device: PyTorch device string (e.g., "cpu", "cuda:0")

    Returns:
        Smoothed vertex positions (N, 3) as numpy float32 array

    Methods:
      - "laplacian": v <- v + weight * (meanNbrs(v) - v)
      - "taubin": v <- v + lambda * L(v); then v <- v + mu * L(v)
      - "none": returns verts unchanged

    Note:
        Requires PyTorch. Install with `pip install torch` or `pip install 'xcat-mesh[gpu]'`
    """
    method = (method or "laplacian").lower()
    if method in {"none", "off", "disable", "disabled"} or num_iter <= 0:
        return verts.astype(np.float32, copy=False)

    try:
        import torch
    except Exception as e:
        raise ImportError(
            "Smoothing requires PyTorch in the current implementation. "
            "Install with `pip install torch` (CPU) or `pip install 'xcat-mesh[gpu]'` (GPU)."
        ) from e

    # Ensure contiguous arrays (marching cubes may return negative strides)
    verts_contig = np.ascontiguousarray(verts)
    faces_contig = np.ascontiguousarray(faces)

    v = torch.tensor(verts_contig, device=device, dtype=torch.float32)
    f = torch.tensor(faces_contig, device=device, dtype=torch.int64)

    A, row_sum = _build_adjacency_torch(f, v.shape[0], device=device)

    for _ in range(int(num_iter)):
        with torch.no_grad():
            if method == "laplacian":
                dv = _laplacian_step_torch(v, A, row_sum)
                v += float(weight) * dv
            elif method == "taubin":
                dv = _laplacian_step_torch(v, A, row_sum)
                v += float(lambda_) * dv
                dv2 = _laplacian_step_torch(v, A, row_sum)
                v += float(mu) * dv2
            else:
                raise ValueError(f"Unknown smoothing method: {method}")

    return v.cpu().numpy().astype(np.float32, copy=False)
