"""Collection of simple example operations built on `TiledOp`.

These operations illustrate how to implement per-window logic using
masked NumPy arrays. Each class implements `__call__(self, data)` where
`data` is a list of masked arrays taken from the current processing window.
"""

import numpy
from numpy import ndarray

from rasterop.tiled_op.tiled_raster_op import TiledOp


class ReplaceMASKEDOP(TiledOp):
    """Replace masked values in the first input with -1.

    Expects at least one input array. All masked pixels in the first input
    are set to -1, preserving other values.
    """

    def __call__(self, data: list[ndarray]):
        """Apply the replacement on the first input array.

        Args:
            data: List of masked arrays for the current window.

        Returns:
            numpy.ma.MaskedArray: The modified first array with masked values
            set to -1.
        """
        if not data or len(data) < 1:
            raise Exception("ReplaceMASKEDOP requires at least one input array")

        result = data[0]
        result[numpy.ma.getmask(result)] = -1
        return result

        


class MedianWithTrickOP(TiledOp):
    """Median with an extra rule: all-zero pixels become nodata.

    After computing the masked median, any pixel location where all bands
    are equal to 0 is set to the operation's `nodata` value.
    """

    def __call__(self, data:list[ndarray]):
        """Compute median and set all-zero pixels to nodata."""
        # we use the masked version of median
        data = numpy.ma.stack(data, axis=0)
        data = numpy.ma.median(data, axis=0)

        # if all the band are 0 we set to na
        mask = numpy.ma.all(data == 0, axis=0)
        data[:, mask] = self.nodata

        return  data




class AnomalyOP(TiledOp):
    """Compute a simple anomaly index from VV and VH channels.

    Produces a single-band output computed as ``(VV * VH) / (VV + VH)``
    for the first two bands of the sole input raster.
    """

    def __init__(self, dtype, nodata):
        """Create an anomaly operation with a single output band."""
        super().__init__(1, dtype, nodata)

    def __call__(self, data:list[ndarray]):
        """Compute the anomaly index from the first input array."""
        if len(data) != 1:
            raise Exception("UnitScaleOP only support one input raster")

        vh = data[0][0]
        vv = data[0][1]

        return ((vv*vh)/(vv+vh))[None,...]

class ThresholdOP(TiledOp):
    """Classify values into categories based on per-category thresholds.

    The second input provides category labels; the first input provides
    continuous values. For each category in `threshold_dic`, pixels where
    `value > threshold` are assigned that category id; others remain nodata.
    Output is `uint8` with `255` as nodata.
    """

    def __init__(self, threshold_dic):
        """Initialize with a mapping: {category_id: threshold_value}."""
        super().__init__(1, numpy.uint8, nodata=255)
        self.threshold_dic=threshold_dic

    def __call__(self, data:list[ndarray]):
        """Apply per-category thresholding.

        Args:
            data: [value_raster, category_raster]
        Returns:
            A `uint8` array with category ids or nodata=255.
        """
        value = data[0]
        categories = data[1]

        # set has 1 as anomaly should ont be bigger
        result  = numpy.ones_like(categories,dtype=value.dtype)*self.nodata
        for category, threshold in self.threshold_dic.items():
            selection = (categories == category) & (value>threshold)
            result[selection] = category

        # value = (value > threshold_array)
        # value = (value < threshold_array)*self.nodata

        return result

