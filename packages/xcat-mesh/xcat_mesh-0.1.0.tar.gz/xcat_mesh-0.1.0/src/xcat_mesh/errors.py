class XcatMeshError(RuntimeError):
    """Base error for xcat-mesh."""

class BinaryMaskError(XcatMeshError):
    """Raised when the input mask is not binary (values must be {0,1})."""

class EmptyMaskError(XcatMeshError):
    """Raised when the mask has no foreground voxels."""

class ConfigError(XcatMeshError):
    """Raised when config is missing required fields or invalid."""
