"""Example tiled operations.

This subpackage contains ready-to-use `TiledOp` implementations demonstrating
how to build custom window-based raster operations.

Modules:
- `s1`: simple statistical and thresholding operations
- `operation`: example time-series operation
- `basic`: basic math/composite operations (add, subtract, multiply, copy first/last non-null, percentiles)
"""

from .operation import MedianOP, DiffSquaredOP, UnitScaleOP, TimeSeriesOp
from .s1 import ReplaceMASKEDOP, MedianWithTrickOP, AnomalyOP, ThresholdOP
from .basic import (
    AddOP,
    SubtractOP,
    MultiplyOP,
    CopyFirstNonNullOP,
    CopyLastNonNullOP,
    PercentileOP,
)
