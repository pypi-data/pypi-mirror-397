# rasterop

Tiled raster processing utilities built on top of Rasterio and NumPy. This repository provides a small, extensible
framework to apply custom operations on large raster datasets in a tiled/streaming fashion.
It includes a generic tiled engine (`tiled_op`) and a few example operations you can adapt to your needs.


## Features
- Process large rasters by windows (tiles) with multi-threaded reading/writing
- Compose custom operations by subclassing `TiledOp`
- Optional masking by geometry or raster mask
- Output tiling aligned to resolution ("target aligned pixels")
- Examples of common operations (median, thresholding, scaling, differences)


## Requirements
- Python 3.12 or newer
- GDAL/GEOS system libraries required by `rasterio` and `shapely` (platform-specific)

Python package dependencies (runtime):
- `rasterio`
- `numpy`
- `shapely`
- `pyproj`
- `tqdm`
- `scipy` (used by `TimeSeriesOp` example)

> Tip (Linux): You may need to install system packages like `gdal`, `geos`, and development headers before 
> `pip install rasterio shapely` will succeed. See Rasterio/Shapely installation docs for your OS.

## Installation
### PyPI
pip install rasterop

### Developement mode
Installation in development mode:
```bash
pip install -e .
```


## License
See `LICENSE.txt` (MIT-style license). Copyright © 2025 CIAT.

## Contributing
Contributions are welcome!
- Please open an issue to discuss substantial changes.
- Feel free to propose improvements to docs, tests, and examples.
