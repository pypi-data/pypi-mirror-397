"""Tiled raster processing engine.

Provides the `TiledOp` base class and the `tiled_op` function to apply
custom operations over large rasters window-by-window with optional
multithreaded I/O, masking, and target-aligned pixels. See the README for
usage examples.
"""
import concurrent.futures
import logging
import math
import os
from abc import abstractmethod, ABC
from contextlib import contextmanager

import numpy
import numpy as np
import rasterio
import threading

from rasterio import windows
from rasterio.coords import disjoint_bounds
from rasterio.enums import Resampling
from rasterio.transform import Affine
from shapely import STRtree, box
from tqdm import tqdm

logger = logging.getLogger(__name__)

class TiledOp(ABC):
    """Abstract base class for tiled operations.

    Subclass this and implement `__call__(self, data)` to define your
    window-by-window processing logic. The engine will pass a list of
    masked arrays (one per input dataset) cropped to the current window.

    Attributes:
        n_band_out (int): Number of bands produced by the operation.
        dtype: NumPy dtype of the output array.
        nodata: NoData value to write for invalid pixels.
    """
    def __init__(self, n_band_out, dtype, nodata):
        self._n_band_out = n_band_out
        self._dtype= dtype
        self._nodata = nodata

    @abstractmethod
    def __call__(self, data):
        """Apply the operation to a list of masked arrays for one window.

        Args:
            data: List of masked ndarrays, one per input raster. Arrays have
                shape `(bands, width, height)` for the current window. Inputs
                outside their bounds are fully masked.

        Returns:
            A masked ndarray with shape `(n_band_out, width, height)`, or None
            to skip writing for this window.
        """
        pass

    @property
    def n_band_out(self):
        """Number of bands produced by this operation."""
        return self._n_band_out

    @property
    def nodata(self):
        """NoData value used in the output dataset."""
        return self._nodata

    @property
    def dtype(self):
        """NumPy dtype of the output array."""
        return self._dtype



def get_image_file(dir_path, extension=None) -> list:
    """List raster files in a directory.

    Args:
        dir_path: Directory path to scan.
        extension: Optional list of filename extensions (without dots) to include.
            Defaults to common GeoTIFF variants: ["tif", "tiff", "TIF", "TIFF"].

    Returns:
        A list of absolute file paths of raster images found in the directory.
    """
    if extension is None:
        extension = ["tif", "tiff", "TIF", "TIFF"]

    # list to store files
    rasters = []
    # Iterate directory
    for file in os.listdir(dir_path):
        file_path = os.path.join(dir_path, file)
        if os.path.isfile(file_path) and (os.path.splitext(file)[-1][1:] in extension):
            rasters.append(file_path)

    return rasters

def global_bounds(datasets, dataset_opener=rasterio.open):
    """Compute the overall bounding box of multiple datasets.

    Args:
        datasets: Iterable of dataset paths or open datasets.
        dataset_opener: Context manager/function used to open each dataset.

    Returns:
        Tuple ``(minx, miny, maxx, maxy)`` representing the union bounds.
    """
    xs = []
    ys = []
    for dataset in datasets:
        with dataset_opener(dataset) as src:
            left, bottom, right, top = src.bounds
        xs.extend([left, right])
        ys.extend([bottom, top])
    return min(xs), min(ys), max(xs), max(ys)


def aligned_bound(bounds, res, target_aligned_pixels):
    """Compute output array width/height from bounds and resolution.

    Optionally adjusts bounds to target-aligned pixels (``-tap`` behavior),
    i.e., snaps the bounds to multiples of the pixel size.

    Args:
        bounds: Tuple ``(minx, miny, maxx, maxy)`` in the target CRS.
        res: Tuple ``(x_res, y_res)`` pixel size.
        target_aligned_pixels: Whether to snap bounds to pixel grid.

    Returns:
        Tuple ``(width, height)`` of the output array in pixels.
    """
    # from the comment taken from rasterio code
    b_w, b_s, b_e, b_n = bounds

    if target_aligned_pixels:
        b_w = math.floor(b_w / res[0]) * res[0]
        b_e = math.ceil(b_e / res[0]) * res[0]
        b_s = math.floor(b_s / res[1]) * res[1]
        b_n = math.ceil(b_n / res[1]) * res[1]

    # Compute output array shape. We guarantee it will cover the output
    # bounds completely
    output_width = int(round((b_e - b_w) / res[0]))
    output_height = int(round((b_n - b_s) / res[1]))

    return output_width, output_height


def process_res(res: object, default: object) -> object:
    """Normalize resolution argument to a 2-tuple.

    Args:
        res: None, scalar, single-item iterable, or 2-tuple.
        default: Fallback resolution to use when `res` is falsy.

    Returns:
        A tuple ``(x_res, y_res)``.
    """
    if not res:
        res = default
    elif not np.iterable(res):
        res = (res, res)
    elif len(res) == 1:
        res = (res[0], res[0])

    return res


def get_dataset_opener(datasets):
    """Return an opener contextmanager for dataset items.

    If the input sequence contains paths, returns `rasterio.open`. If it
    contains already opened datasets or file-like objects, returns a no-op
    context manager that yields the object as-is.
    """
    # Create a dataset_opener object to use in several places in this function.
    if isinstance(datasets[0], (str, os.PathLike)):
        dataset_opener = rasterio.open
    else:
        # No op opener, return the object and do nothing I think assum a dataset has been given
        @contextmanager
        def nullcontext(obj):
            try:
                yield obj
            finally:
                pass

        dataset_opener = nullcontext

    return dataset_opener


def extract_dataset_info(dataset, opener):
    """Read basic metadata from a dataset.

    Args:
        dataset: Path or open dataset object.
        opener: Context manager/callable used to open the dataset.

    Returns:
        Tuple ``(profile, res, nodataval, dtype, colormap)`` where:
        - ``profile`` is the full rasterio profile dict
        - ``res`` is the pixel size tuple
        - ``nodataval`` is the first band's nodata value (or None)
        - ``dtype`` is the first band's dtype string
        - ``colormap`` is the colormap dict for band 1 or None
    """
    with opener(dataset) as src:
        profile = src.profile
        res = src.res
        nodataval = src.nodatavals[0]
        dt = src.dtypes[0]

        try:
            colormap = src.colormap(1)
        except ValueError:
            colormap = None

    return profile, res, nodataval, dt, colormap


# TODO each thread in this version as it own reader
# TODO Check multiple writer in r+ mode to see perf
def tiled_op(
        datasets,
        op,
        output_count,
        dst_path,
        mask_geom=None,
        mask_raster=None,
        bounds=None,
        res=None,
        nodata=None,
        dtype=None,
        indexes=None,
        resampling=Resampling.nearest,
        target_aligned_pixels=False,
        dst_kwds=None,
        src_kwds=None,
        num_workers=2,
        window_size=None
):
    """Run a tiled operation over one or more input rasters and write the result.

    Iterates the output image by windows, reads the corresponding window from
    each input dataset (with optional resampling and masks), calls the provided
    `op` with the list of masked arrays, and writes the returned array to the
    destination. If `dst_path` is None, returns the in-memory output and its
    transform instead of writing to disk.

    Args:
        datasets: List of dataset paths or already-open datasets to read from.
        op: Callable that takes a list of masked arrays (one per input dataset)
            and returns a masked array to write. The callable is invoked for
            each output window.
        output_count: Number of bands in the output dataset.
        dst_path: Output path. If None, an in-memory dataset and its transform
            are returned instead of writing to disk.
        mask_geom: Optional Shapely geometry to restrict processing to
            intersecting windows.
        mask_raster: Optional path or dataset providing a raster mask. Pixels
            masked by this raster are set to the destination nodata.
        bounds: Optional tuple ``(left, bottom, right, top)`` defining output
            extent. Defaults to the union of input bounds.
        res: Optional resolution. May be a single float or a 2-tuple
            ``(x_res, y_res)``. Defaults to the first input's resolution.
        nodata: Optional nodata value for the output. Defaults to the first
            input's nodata.
        dtype: Optional output dtype. Defaults to the first input's dtype.
        indexes: Optional band index or list of indexes to read from sources.
        resampling: Resampling algorithm used when reading inputs. Defaults to
            `Resampling.nearest`.
        target_aligned_pixels: If True, adjust bounds so pixel coordinates are
            aligned to integer multiples of pixel size (GDAL `-tap` behavior).
        dst_kwds: Optional dict of creation options to overlay on the output
            profile.
        src_kwds: Optional dict of keyword arguments forwarded to open sources.
        num_workers: Number of worker threads used to process windows.
        window_size: Optional fixed window size (pixels). If not provided, use
            dataset-native block windows.

    Returns:
        tuple: A pair ``(dst, out_transform)`` when `dst_path` is None, where
            `dst` is an open in-memory dataset and `out_transform` is the
            destination affine transform. When `dst_path` is provided, returns
            `None`.

    Raises:
        Exception: Propagates exceptions raised by the operation callable or
            I/O operations during reading/writing.
    """


    # manage inpute
    dataset_opener = get_dataset_opener(datasets)

    first_profile, first_res, first_nodataval, first_dt, first_colormap = extract_dataset_info(datasets[0],
                                                                                                            dataset_opener)

    # Extent from option or extent of all inputs
    if not bounds:
        dst_w, dst_s, dst_e, dst_n = global_bounds(datasets, dataset_opener)
    else:
        dst_w, dst_s, dst_e, dst_n = bounds

    if src_kwds is None:
        src_kwds = {}

    # Resolution/pixel size
    res = process_res(res, first_res)

    output_width, output_height = aligned_bound((dst_w, dst_s, dst_e, dst_n), res, target_aligned_pixels)
    output_transform = Affine.translation(dst_w, dst_n) * Affine.scale(res[0], -res[1])

    if dtype is not None:
        dt = dtype
        logger.debug("Set dtype: %s", dt)
    else:
        dt = first_dt

    out_profile = first_profile
    out_profile.update(**(dst_kwds or {}))

    out_profile["transform"] = output_transform
    out_profile["height"] = output_height
    out_profile["width"] = output_width
    out_profile["count"] = output_count
    out_profile["dtype"] = dt
    if nodata is not None:
        out_profile["nodata"] = nodata

    # todo used in rasterio not so sur why
    #nodataval = check_no_data(nodata, dt)

    #

    # read_lock = threading.Lock()
    write_lock = threading.Lock()

    ## TODO manage block better
    # create an empty raster

    with rasterio.open(dst_path, mode="w", **out_profile) as dst:
        dst_transform = dst.transform

        if window_size is None:
            windows_list = [window for ij, window in dst.block_windows()]
        else:
            windows_list = create_grid_windows(dst.width, dst.height, window_size)

        if mask_geom:
            tree = STRtree([box(*rasterio.windows.bounds(w, dst_transform)) for w in windows_list])
            windows_index = tree.query(mask_geom, predicate="intersects")[1] # index 1 is tree elements
            windows_list = [windows_list[i] for i in windows_index ]

        windows_dataset=[]
        try:
            src_dt = [(dataset_opener(dataset, "r", **src_kwds), dataset) for dataset in datasets]

            # if no dataset intersect this area we skip it completely # todo could use a while loop to avoid check
            for window in windows_list:
                inter_win= []
                for src, dataset in src_dt:
                    dst_bounds = rasterio.windows.bounds(window, dst_transform)
                    if not disjoint_bounds(dst_bounds, src.bounds):
                        inter_win.append(dataset)
                if len(inter_win)>0:  # If 1 window intersect we use all
                    windows_dataset.append((window, datasets))

        finally:
            for reader, _ in src_dt:
                reader.close()

        job = lambda win: process_windows(dst,
                                          dataset_opener,
                                          src_kwds,
                                          mask_raster,
                                          win,
                                          dst_transform,
                                          indexes,
                                          resampling,
                                          op,
                                          write_lock)

        with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
            list(tqdm(executor.map(job, windows_dataset), total=len(windows_dataset)))

        if dst_path is None:
            return dst, output_transform

        else:
            if first_colormap:
                dst.write_colormap(1, first_colormap)
                return None
            return None


def create_grid_windows(width, height, window_size):
    """Create a list of windows covering the entire image with fixed size.

    Args:
        width: Image width in pixels
        height: Image height in pixels
        window_size: Size of square windows in pixels

    Returns:
        List of rasterio.windows.Window objects
    """
    windows_list = []
    for y in range(0, height, window_size):
        for x in range(0, width, window_size):
            window_height = min(window_size, height - y)
            window_width = min(window_size, width - x)
            windows_list.append(windows.Window(x, y, window_width, window_height))
    return windows_list


def process_windows(dst,
                    dataset_opener,
                    src_kwds,
                    mask_raster,
                    window_datasets,
                    window_transform,
                    indexes,
                    resampling,
                    op,
                    write_lock
                    ):
    """Process a single output window: read sources, apply op, and write.

    This function is intended to be executed in worker threads. It reads the
    corresponding window from each source dataset (and optional mask raster),
    calls the provided operation with the list of masked arrays, and writes the
    operation result to the destination dataset.

    Args:
        dst: Open rasterio dataset in write mode.
        dataset_opener: Callable/context manager to open input datasets.
        src_kwds: Dict of keyword args passed to dataset opener for sources.
        mask_raster: Optional path or dataset to a raster mask.
        window_datasets: Tuple ``(window, datasets)`` pairing the window to
            process and the list of source datasets for that window.
        window_transform: Affine transform of the destination dataset.
        indexes: Optional band indexes to read from sources.
        resampling: Resampling method for reading sources.
        op: Callable implementing the tiled operation.
        write_lock: Threading lock to serialize writes to the destination.
    """

    window = window_datasets[0]
    datasets = window_datasets[1]
    mask=None
    try:
        readers = [dataset_opener(dataset, "r", **src_kwds) for dataset in datasets]

        dst_bounds = rasterio.windows.bounds(window, window_transform)
        dst_w, dst_s, dst_e, dst_n = dst_bounds

        # read mask value for windows
        mask_reader=None
        if mask_raster:
            mask_reader = dataset_opener(mask_raster, "r", **src_kwds)

            src_window = windows.from_bounds(dst_w, dst_s, dst_e, dst_n, mask_reader.transform)
            src_window_rnd_shp = src_window.round_lengths()

            mask = mask_reader.read(
                out_shape=(mask_reader.count, window.height, window.width),
                window=src_window_rnd_shp,
                boundless=True,
                masked=True,
                indexes=indexes,
                resampling=Resampling.nearest)

            # early exist if no valid pixel
            if np.all(mask == False):
                return # this should go to finally

        region = []
        result = None
        for src in readers:
            target_shape = (src.count, window.height, window.width)
            #Chekc if it works to remove i expect fully mapped dataset
            #if disjoint_bounds(dst_bounds, src.bounds):
            #    continue

            src_window = windows.from_bounds(dst_w, dst_s, dst_e, dst_n, src.transform)
            src_window_rnd_shp = src_window.round_lengths()

            data = src.read(
                out_shape=target_shape,
                window=src_window_rnd_shp,
                boundless=True,
                masked=True,
                indexes=indexes,
                resampling=resampling)

            region.append(data)


        result = op(region)

        if mask_raster:
            result=np.where(numpy.invert(mask.mask), result, dst.nodata)

        if result is not None:
            with write_lock:
                dst.write(result, window=window)


    finally:
        if mask_reader:
            mask_reader.close()

        for reader in readers:
            reader.close()






class TiledOPExecutor:
    """Small helper to configure defaults and run a `TiledOp`.

    This class lets you set common parameters (resolution, resampling,
    threading, etc.) once and reuse them across multiple executions.
    """

    def __init__(self,
                 res=None,
                 indexes=None,
                 resampling=Resampling.nearest,
                 target_aligned_pixels=False,
                 dst_kwds=None,
                 src_kwds=None,
                 num_workers=2,
                 window_size=None):
        """Initialize executor defaults.

        Args:
            res: Output resolution (scalar or 2-tuple). If None, inferred from first raster.
            indexes: Band indexes to read from inputs (None = all bands).
            resampling: Resampling method when reading inputs.
            target_aligned_pixels: Snap output bounds to pixel grid (``-tap``).
            dst_kwds: Dict of creation options to overlay on output profile.
            src_kwds: Dict of options passed when opening sources.
            num_workers: Number of worker threads for I/O and processing.
            window_size: Size of processing windows in pixels (square). If None, auto-chosen.
        """

        self.res = res
        self.indexes = indexes
        self.resampling = resampling
        self.target_aligned_pixels = target_aligned_pixels
        self.dst_kwds = dst_kwds
        self.src_kwds = src_kwds
        self.num_workers = num_workers
        self.window_size = window_size

    def execute(self,
                operation: TiledOp,
                rasters,
                outpath,
                bounds=None,
                mask_geo=None,
                mask_raster=None):
        """Execute a `TiledOp` over input rasters and write to `outpath`.

        Args:
            operation: Instance of a `TiledOp` subclass to apply.
            rasters: Sequence of raster paths (or open datasets).
            outpath: Path of the output raster to write.
            bounds: Optional output bounds (minx, miny, maxx, maxy). If None, union of inputs.
            mask_geo: Optional Shapely geometry to mask processing area.
            mask_raster: Optional raster mask path or dataset.
        """

        tiled_op(
                rasters,
                operation,
                operation.n_band_out,
                outpath,
                bounds=bounds,
                mask_geom=mask_geo,
                mask_raster=mask_raster,
                res=self.res,
                nodata=operation.nodata,
                dtype=operation.dtype,
                indexes=self.indexes,
                resampling=self.resampling,
                target_aligned_pixels=self.target_aligned_pixels,
                dst_kwds=self.dst_kwds,
                src_kwds=self.src_kwds,
                num_workers=self.num_workers,
                window_size=self.window_size)

