"""Tiled operations engine for rasterop.

This subpackage exposes the tiled processing engine (`tiled_raster_op`) and
ready-to-use example operations under `operation`.

Convenience imports:
- `TiledOp`: Base class for custom operations
- `tiled_op`: Core windowed processing function
- `TiledOPExecutor`: Small helper to run an operation
"""

from .tiled_raster_op import TiledOp, tiled_op, TiledOPExecutor  # noqa: F401
