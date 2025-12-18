from pathlib import Path

import numpy as np
import rasterio


from rasterop.tiled_op import TiledOp


class BinaryMap(TiledOp):
    """
    Merge the raser list by copying the first valid value from the raster list
    """

    def __init__(self, target, dtype="int16", nodata=-1):
        """
        :param n_category: number of categories of the categorised map
        :param dtype: output dtype to use for the output raster
        :param nodata: No data value to use
        """
        super().__init__(1, dtype, nodata)
        self.target = target

    def __call__(self, data):
        """Returns the first available pixel."""
        if len(data) > 0:
            _, width, height = data[0].shape
            result = np.full((1, width, height), self.nodata)
            #print(np.ma.getmask(result))
            d = data[0]
            mask = np.logical_not(np.logical_or(np.ma.getmask(d), np.isnan(d)))
            np.equal(d, self.target, where=mask, casting="unsafe", out=result)

            return result

        return None


class MergeCopyFirst(TiledOp):
    """
    Merge the raser list by copying the first valid value from the raster list
    """

    def __init__(self, n_band, dtype="float32", nodata=-1):
        """
        :param n_category: number of categories of the categorised map
        :param dtype: output dtype to use for the output raster
        :param nodata: No data value to use
        """
        super().__init__(n_band, dtype, nodata)

    @classmethod
    def same_as(cls, path: Path):
        """create a merge operation using the same type no data and band as the reference raster."""

        with rasterio.open(path) as src:
            nodata = src.nodata
            dtype = src.profile['dtype']
            count = src.count

        return cls(count, dtype, nodata)

    def __call__(self, data):
        """Returns the first available pixel."""
        if len(data) > 0:
            bands, width, height = data[0].shape
            result = np.full((bands, width, height), self.nodata)
            #print(np.ma.getmask(result))
            for i, d in enumerate(reversed(data)):
                mask = np.logical_not(np.logical_or(np.ma.getmask(d), np.isnan(d)))
                np.copyto(result, d, where=mask, casting="unsafe")

            return result

        return None

class CountCategoryToBand(TiledOp):
    """The function receive a list of categorised raster with value fom 0 to n categories -1 and count the number of
    time each category appear. The count is saved to the band corresponding to the categories number"""
    def __init__(self, max_val, dtype="int16", nodata=-1, percent= True):
        """

        :param max_val: max value, we assume category run from 0 to n
        :param dtype: output dtype to use for the output raster
        :param nodata: No data value to use
        :param percent: if True save the results as a percentage, for false, save the counts
        """
        super().__init__(max_val+1, dtype, nodata)
        # self.val_max = max_val
        self.percent = percent

    def __call__(self, data):
        """
        For each pixel count the number of time value (integer) appear, copy the number of occurence of value i to band
        i
        """
        _, width, height = data[0].shape
        # init count at 0
        result = np.zeros((self.n_band_out, width, height))
        #nothing masked
        mask = np.zeros((width, height), np.bool_)

        for d in data:
            # we need the 0 because d can have more band
            np.logical_or(mask, np.ma.getmask(d)[0], out=mask)
            for i in range(self.n_band_out):
                result[i] += np.where(d[0] == i, 1, 0)

        if self.percent:
            result = (result / len(data) * 100).astype(self.dtype)

        for b in range(self.n_band_out):
            result[b, mask] = self.nodata

        # np.copyto(result, d, where=np.logical_not(np.ma.getmask(d)), casting="unsafe")

        return result


class MapCategoryThreshold(TiledOp):
    """
    "Generate a binary map with value 1 where the target category appear threshold time or more
    :param data:
    :param target:
    :param count:
    :return:
    """

    def __init__(self, target, threshold, dtype="int16", nodata=-1):
        """

        :param target: category to threshold
        :param threshold: count equal of bigger than this threshold is mapped as true
        :param dtype: Output type
        :param nodata:
        """
        super().__init__(1, dtype, nodata)
        self.threshold = threshold
        self.target = target


    def __call__(self, data):
        # We work with first band of the data
        _, width, height = data[0].shape
        result = np.full((1, width, height), self.nodata)
        mask = np.zeros((1, width, height))
        for d in data:
            np.logical_or(mask, np.ma.getmask(d)[0], out=mask)
            result[0] += np.where(d[0] == self.target, 1, 0)
            # np.copyto(result, d, where=np.logical_not(np.ma.getmask(d)), casting="unsafe")
        result[0] = np.where(result >= self.count, 1, 0)
        result[mask] = self.nodata
        return result.astype(self.dtype)

class MaxCategory(TiledOp):
    """
    For each pixel of (the merged map (band number = category, band value = score)(for example result of
    CountCategoryToBand) count the most usual category and
    score and save it to band 1 and 2 respectively.
    :param data:
    :return:
    """

    def __init__(self, dtype="int16", nodata=-1):
        super().__init__(1, dtype, nodata)

    def __call__(self, data):
        #We assum data is a list of length 1
        data = data[0]

        _, width, height = data.shape
        result = np.full((1, width, height), self.nodata)
        mask = np.zeros((1, width, height), np.bool_)

        result[0] = np.argmax(data, axis=0)
        #result[1] = np.amax(data[0], axis=0)
        # loop on band and apply mask
        for b in range(len(data)):
            np.logical_or(mask, np.ma.getmask(data)[b], out=mask)


        result[mask] = self.nodata
        return result.astype(self.dtype)

class MaxScore(TiledOp):
    """
    For each pixel of (the merged map (band number = category, band value = score)(for example result of
     CountCategoryToBand) count the most usual category and
    score and save it to band 1 and 2 respectively.
    :param data:
    :return:
    """

    def __init__(self, dtype="int16", nodata=-1):
        super().__init__(1, dtype, nodata)

    def __call__(self, data):
        # data is a list of length 1
        data = data[0]
        _, width, height = data.shape
        result = np.full((1, width, height), self.nodata)

        mask = np.zeros((1, width, height), np.bool_)

        result[0] = 100*np.amax(data, axis=0)

        for b in range(len(data)):
            np.logical_or(mask, np.ma.getmask(data)[b], out=mask)

        result[mask] = self.nodata

        return result.astype(self.dtype)

class MaxCategoryAndScore(TiledOp):
    """
    For each pixel of (the merged map (band number = category, band value = score)(for example result of
     CountCategoryToBand) count the most usual category and
    score and save it to band 1 and 2 respectively.
    :param data:
    :return:
    """

    def __init__(self, dtype="int16", nodata=-1):
        super().__init__(2, dtype, nodata)

    def __call__(self, data):
        # assum data is of lenght 1
        data = data[0]

        _, width, height = data.shape
        result = np.full((2, width, height),  self.nodata)
        mask = np.zeros((width, height), np.bool_)

        result[0] = np.argmax(data, axis=0)
        result[1] = np.amax(data, axis=0)

        for b in range(len(data)):
            np.logical_or(mask, np.ma.getmask(data)[b], out=mask)

        result[0][mask] = self.nodata
        result[1][mask] = self.nodata

        return result.astype(self.dtype)

class AverageTiffs(TiledOp):
    """
    Match pixe; per band and average them
    :param data:
    :return:
    """

    def __init__(self, nband, dtype="int16", nodata=-1):
        super().__init__(nband, dtype, nodata)

    def __call__(self, data):
        return np.ma.mean(np.array(data),axis=0)


