"""
Definition of supported output formats via GDAL.
"""

SUPPORTED_FORMATS = {
    "GeoTIFF": {
        "driver": "GTiff",
        "extension": ".tif",
        "description": "Standard GeoTIFF — universal geospatial raster format",
        "creation_options": ["COMPRESS=LZW", "TILED=YES", "BIGTIFF=IF_NEEDED"],
        "color": "cyan",
    },
    "COG": {
        "driver": "GTiff",
        "extension": ".tif",
        "description": "Cloud-Optimized GeoTIFF — optimized for cloud streaming",
        "creation_options": [
            "COMPRESS=LZW",
            "TILED=YES",
            "BIGTIFF=IF_NEEDED",
            "COPY_SRC_OVERVIEWS=YES",
        ],
        "cog": True,
        "color": "bright_cyan",
    },
    "PNG": {
        "driver": "PNG",
        "extension": ".png",
        "description": "Portable Network Graphics — lossless, good for visualization",
        "creation_options": [],
        "color": "green",
    },
    "JPEG": {
        "driver": "JPEG",
        "extension": ".jpg",
        "description": "JPEG — lossy compression, small file size",
        "creation_options": ["QUALITY=90"],
        "color": "yellow",
    },
    "NetCDF": {
        "driver": "netCDF",
        "extension": ".nc",
        "description": "Network Common Data Form — multidimensional scientific format",
        "creation_options": [],
        "color": "blue",
    },
    "HFA": {
        "driver": "HFA",
        "extension": ".img",
        "description": "Erdas Imagine — proprietary raster format common in GIS",
        "creation_options": ["COMPRESSED=YES"],
        "color": "magenta",
    },
    "ENVI": {
        "driver": "ENVI",
        "extension": ".bin",
        "description": "ENVI Format — used in hyperspectral remote sensing",
        "creation_options": [],
        "color": "red",
    },
    "VRT": {
        "driver": "VRT",
        "extension": ".vrt",
        "description": "GDAL Virtual Format — virtual reference file",
        "creation_options": [],
        "color": "white",
    },
    "GPKG": {
        "driver": "GPKG",
        "extension": ".gpkg",
        "description": "GeoPackage — OGC container for rasters and vectors",
        "creation_options": [],
        "color": "bright_green",
    },
    "WebP": {
        "driver": "WEBP",
        "extension": ".webp",
        "description": "WebP — modern high-compression format for the web",
        "creation_options": ["QUALITY=85"],
        "color": "bright_yellow",
    },
    "PDF": {
        "driver": "PDF",
        "extension": ".pdf",
        "description": "Geospatial PDF — portable and georeferenced sharing standard",
        "creation_options": ["GEO_ENCODING=ISO32000"],
        "color": "white",
    },
    "JPEG2000": {
        "driver": "JP2OpenJPEG",
        "extension": ".jp2",
        "description": "JPEG2000 — standard wavelet compression",
        "creation_options": ["QUALITY=85"],
        "color": "bright_cyan",
    },
    "BMP": {
        "driver": "BMP",
        "extension": ".bmp",
        "description": "Windows Bitmap — classic bitmap format",
        "creation_options": [],
        "color": "bright_yellow",
    },
}

# Supported input formats for the converter
SUPPORTED_INPUT_EXTENSIONS = [
    ".jp2", ".j2k", ".j2c", ".jpx",  # JPEG2000
    ".tif", ".tiff",                 # GeoTIFF
    ".ecw",                          # ECW (Enhanced Compression Wavelet)
    ".img",                          # HFA / Erdas
    ".nc",                           # NetCDF
    ".png",                          # PNG
    ".jpg", ".jpeg",                 # JPEG
    ".ntf", ".nitf",                 # NITF
    ".hdf", ".h5",                   # HDF
    ".vrt",                          # VRT
    ".dem", ".asc",                  # Classic DEMs
]
