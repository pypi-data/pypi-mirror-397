"""Basic raster math and selection operations built on `TiledOp`.

All operations are mask-aware and expect inputs as a list of masked arrays
with shape `(bands, width, height)` for the current processing window.

Notes:
    - Unless otherwise noted, operations accept N inputs and apply the
      reduction across the stack on axis 0.
    - For pairwise-only operations (e.g., subtraction), exactly two inputs are
      required.
    - Constructors follow the library convention: set `n_band_out`, `dtype`,
      and `nodata`. When not obvious, `n_band_out` should typically match the
      number of bands from inputs, but this module leaves that check to the
      caller.
"""

import warnings
from pathlib import Path

import numpy
import numpy as np
import numpy.ma as ma
import rasterio
from numpy.typing import NDArray

from rasterop.tiled_op.tiled_raster_op import TiledOp

MaskPolicy = str  # "strict" or "lenient"


class AddOP(TiledOp):
    """Elementwise sum across all inputs (mask-aware).

    Uses masked-sum so that masked values do not contribute. Masking policy:
    - strict (default): mask if ANY input is masked at a pixel
    - lenient: mask only if ALL inputs are masked at a pixel
    """

    def __init__(self, n_band_out, dtype=np.float32, nodata=np.nan, mask_policy: MaskPolicy = "strict"):
        super().__init__(n_band_out, dtype, nodata)
        self.mask_policy = mask_policy

    def __call__(self, data: list[NDArray]):
        """Sum inputs elementwise with mask handling.

        Args:
            data: List of masked arrays of identical shape `(bands, width, height)`.

        Returns:
            numpy.ma.MaskedArray: Elementwise sum with mask aggregated per
            `mask_policy`.
        """
        if len(data) < 2:
            raise Exception("AddOP requires at least two input raster")
        stacked = ma.stack(data, axis=0)
        out = ma.sum(stacked, axis=0)
        # adjust mask per policy
        m = ma.getmaskarray(stacked)
        if self.mask_policy == "strict":
            out.mask = m.any(axis=0)
        else:
            out.mask = m.all(axis=0)
        return out.astype(self.dtype, copy=False)


class SubtractOP(TiledOp):
    """Pairwise subtraction: data[0] - data[1] (mask-aware).

    Masking policy:
    - strict (default): mask if ANY input is masked at a pixel
    - lenient: mask only if BOTH inputs are masked at a pixel
    """

    def __init__(self, n_band_out, dtype=np.float32, nodata=np.nan, mask_policy: MaskPolicy = "strict"):
        super().__init__(n_band_out, dtype, nodata)
        self.mask_policy = mask_policy

    def __call__(self, data: list[NDArray]):
        """Subtract the second input from the first with mask handling.

        Args:
            data: Two masked arrays of identical shape `(bands, width, height)`.

        Returns:
            numpy.ma.MaskedArray: Elementwise subtraction with mask aggregated
            per `mask_policy`.
        """
        if len(data) != 2:
            raise Exception("SubtractOP requires exactly two input rasters")
        a, b = data[0], data[1]
        out = ma.subtract(a, b)
        ma_a = ma.getmaskarray(a)
        ma_b = ma.getmaskarray(b)
        if self.mask_policy == "strict":
            out.mask = ma_a | ma_b
        else:
            out.mask = ma_a & ma_b
        return out.astype(self.dtype, copy=False)

class RasterToBandOP(TiledOp):
    """Append each raster to a different band."""

    def __call__(self, data: list[NDArray]):
        """Multiply inputs elementwise with mask handling.

        Args:
            data: List of masked arrays of identical shape `(bands, width, height)`.

        Returns:
            numpy.ma.MaskedArray: Elementwise product with mask aggregated per
            `mask_policy`.
        """
        if len(data) < 1:
            raise Exception("RasterToBandOP requires at least one input raster")

        out = numpy.ma.stack(data, axis=0, dtype=self.dtype)

        return out

class MultiplyOP(TiledOp):
    """Elementwise product across all inputs (mask-aware).

    Masking policy:
    - strict (default): mask if ANY input is masked at a pixel
    - lenient: mask only if ALL inputs are masked at a pixel
    """

    def __init__(self, n_band_out, dtype=np.float32, nodata=np.nan, mask_policy: MaskPolicy = "strict"):
        super().__init__(n_band_out, dtype, nodata)
        self.mask_policy = mask_policy

    def __call__(self, data: list[NDArray]):
        """Multiply inputs elementwise with mask handling.

        Args:
            data: List of masked arrays of identical shape `(bands, width, height)`.

        Returns:
            numpy.ma.MaskedArray: Elementwise product with mask aggregated per
            `mask_policy`.
        """
        if len(data) < 1:
            raise Exception("MultiplyOP requires at least one input raster")

        stacked = ma.stack(data, axis=0, dtype=self.dtype)
        out = ma.prod(stacked, axis=0)
        m = ma.getmaskarray(stacked)
        if self.mask_policy == "strict":
            out.mask = m.any(axis=0)
        else:
            out.mask = m.all(axis=0)
        return out


class CopyFirstNonNullOP(TiledOp):
    """Copy the first non-masked pixel across inputs for each band/pixel.

    If all inputs are masked at a pixel, the output pixel is masked.
    """

    def __init__(self, n_band_out, dtype=np.float32, nodata=np.nan):
        super().__init__(n_band_out, dtype, nodata)

    @classmethod
    def same_as(cls, path: Path):
        """create a merge operation using the same type no data and band as the reference raster."""

        with rasterio.open(path) as src:
            nodata = src.nodata
            dtype = src.profile['dtype']
            count = src.count

        return cls(count, dtype, nodata)

    def __call__(self, data: list[NDArray]):
        """Copy first non-masked values across inputs.

        Args:
            data: List of masked arrays with identical shapes `(bands, width, height)`.

        Returns:
            numpy.ma.MaskedArray: Array where each pixel/band is taken from the
            first input that is not masked at that location.
        """
        if len(data) < 1:
            raise Exception("CopyFirstNonNullOP requires at least one input raster")
        # Start with a fully masked array of the correct shape
        result = ma.masked_all_like(data[0])

        # we need to check if no data is not an issue
        # previous code
        # bands, width, height = data[0].shape
        #     result = np.full((bands, width, height), self.nodata)
        #     #print(np.ma.getmask(result))
        #     for i, d in enumerate(reversed(data)):
        #         mask = np.logical_not(np.logical_or(np.ma.getmask(d), np.isnan(d)))
        #         np.copyto(result, d, where=mask, casting="unsafe")


        for arr in data:
            # Fill only where result is masked
            sel = ma.getmaskarray(result)
            if sel is ma.nomask:
                # already filled everywhere
                break
            result[sel] = arr[sel]
        return result

class CopyLastNonNullOP(CopyFirstNonNullOP):
    """Copy the last non-masked pixel across inputs for each band/pixel.

    Later inputs override earlier ones when they are not masked.
    """

    def __init__(self, n_band_out, dtype=np.float32, nodata=np.nan):
        super().__init__(n_band_out, dtype, nodata)

    def __call__(self, data: list[NDArray]):
        """Copy last non-masked values across inputs.

        Args:
            data: List of masked arrays with identical shapes `(bands, width, height)`.

        Returns:
            numpy.ma.MaskedArray: Array where each pixel/band is taken from the
            last input that is not masked at that location.
        """
        data.reverse()
        return super().__call__(data)


class PercentileOP(TiledOp):
    """Compute per-pixel percentile(s) across inputs (mask-aware).

    Args:
        q: Percentile or sequence of percentiles in [0, 100]. If multiple
            percentiles are provided, the output will stack them on the first
            dimension (like bands), i.e., shape `(Q, bands, width, height)`;
            set `n_band_out` accordingly if you plan to flatten/reshape.
        dtype: Output dtype.
        nodata: Output nodata value.

    Notes:
        Uses `nanpercentile` over a float view where masked values are
        converted to NaN. The output mask is set where all inputs were masked.
    """

    def __init__(self, q: float | list[float] | NDArray, dtype, nodata):
        n_band = len(q) if isinstance(q, (list, np.ndarray)) else 1
        super().__init__(n_band, dtype, nodata)
        self.q = np.asarray(q, dtype=float)

    def __call__(self, data: list[NDArray]):
        if len(data) < 1:
            raise Exception("PercentileOP requires at least one input raster")
        stacked = ma.stack(data, axis=0)  # (N, B, W, H)
        mask = ma.getmaskarray(stacked)
        # Convert to float with NaNs for masked values
        arr = stacked.astype(float).filled(np.nan)
        # Compute percentiles along the stack axis (0)
        # Suppress spurious RuntimeWarning from NumPy when a slice is all-NaN;
        # we explicitly track mask via `all_masked` below.
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                message="All-NaN slice encountered",
                category=RuntimeWarning,
                module=r"numpy\.lib\._nanfunctions_impl"
            )
            p = np.nanpercentile(arr, self.q, axis=0)  # shape: (Q?, B, W, H)
        all_masked = np.all(mask, axis=0)

        if p.ndim == 3:
            # single percentile: (B, W, H)
            out = p.astype(self.dtype, copy=False)
            result = ma.masked_array(out, mask=all_masked)
            return result
        else:
            # multiple percentiles: keep (Q, B, W, H) 4D output
            Q, B, W, H = p.shape
            out = p.astype(self.dtype, copy=False)
            mask_qb = np.broadcast_to(all_masked, (Q, B, W, H))
            result = ma.masked_array(out, mask=mask_qb)
            return result
