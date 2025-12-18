"""Example of a multi-date time series operation built on `TiledOp`.

This module demonstrates how to aggregate statistics across a list of
window arrays, where each input dataset represents a different date.
"""
import numpy
import numpy as np
import scipy

from rasterop.tiled_op.tiled_raster_op import TiledOp



class MedianOP(TiledOp):
    """Compute the per-pixel median across all inputs (mask-aware)."""

    def __call__(self, data: list[np.ndarray]):
        """Compute the masked median across the input stack.

        Args:
            data: List of masked arrays (one per input), each shaped
                `(bands, width, height)` for the current window.

        Returns:
            numpy.ma.MaskedArray: Median across inputs computed along axis 0,
                with masks propagated.
        """
        # we use the masked version of median
        data = numpy.ma.stack(data, axis=0)
        return numpy.ma.median(data, axis=0)

class DiffSquaredOP(TiledOp):
    """Return squared difference of two inputs: (baseline - detection) ** 2.

    Requires exactly two input rasters.
    """

    def __call__(self, data: list[np.ndarray]):
        """Compute squared difference between the two input arrays.

        Args:
            data: Exactly two masked arrays `(baseline, detection)` with shape
                `(bands, width, height)`.

        Returns:
            numpy.ma.MaskedArray | numpy.ndarray: Elementwise squared difference
            `(baseline - detection) ** 2`, preserving the input mask behavior.
        """
        if len(data) != 2:
            raise Exception("DiffSquared only support two input raster")

        baseline = data[0]
        detection = data[1]

        return (baseline - detection) ** 2

class UnitScaleOP(TiledOp):
    """Scale values to [0, 1] range per band using provided low/high per band.

    `low` and `high` are arrays of shape `(bands,)` matching the number of
    bands in the input. Values are linearly scaled by `(x - low) / (high - low)`.
    """

    def __init__(self, low, high, n_band_out, dtype, nodata):
        """Initialize the scaler.

        Args:
            low: 1D array-like of per-band lower bounds.
            high: 1D array-like of per-band upper bounds.
            n_band_out: Number of output bands.
            dtype: Output dtype.
            nodata: Output nodata value.
        """
        super().__init__(n_band_out, dtype, nodata)
        self.low=low
        self.high=high

    def __call__(self, data:list[np.ndarray]):
        """Apply per-band unit scaling to a single input raster.

        Expects exactly one input array of shape `(bands, width, height)`.
        """
        if len(data) != 1:
            raise Exception("UnitScaleOP only support one input raster")

        img = data[0]
        # Ensure low and high are shaped for broadcasting: (band, 1, 1)
        low = self.low[:, None, None]
        high = self.high[:, None, None]
        # Numerator: img - low (per band). Denominator: (high - low) per band
        return (img - low) / (high - low)


class TimeSeriesOp(TiledOp):
    """Compute simple statistics across a time series of windows.

    Each input dataset is assumed to be a date in the time series. This
    example outlines how one might compute medians, standard deviations,
    and correlation-like metrics across dates for the first two bands.

    Note: The implementation here is illustrative and may need adaptation
    for real use (e.g., shapes/axes handling and pearson computation). It
    intentionally avoids behavioral changes as per the current task.
    """
    def __init__(self):
        """Initialize with 5 output bands (example layout)."""
        super().__init__(5, np.float32, 0)

    def __call__(self, data):
        """Apply the time series operation over the provided window stack.

        Args:
            data: List of masked arrays, one per date, each shaped
                `(bands, width, height)`.

        Returns:
            A masked array of shape `(n_band_out, width, height)` containing
            the computed statistics, or `None` if `data` is empty.
        """
        if len(data) > 0:
            _, width, height = data[0].shape
            result = np.full((1, width, height), self.nodata)

            stacked_b0 = np.stack([d[0] for d in data])
            stacked_b1 = np.stack([d[1] for d in data])

            # Example statistics (axes may require adaptation for real data):
            # result[0] = stacked_b0.mean(axis=1)
            result[0] = np.median(stacked_b0, axis=1),
            result[1] = np.median(stacked_b1, axis=1),
            result[2] = stacked_b0.std(ddof=1, axis=1),
            result[3] = stacked_b1.std(ddof=1, axis=1),
            result[4]= scipy.pearsonr(stacked_b0,stacked_b1,axis=0)

            mask = np.logical_or.reduce([d.mask for d in data])

            return  np.ma.masked_array(result, mask)

        return None