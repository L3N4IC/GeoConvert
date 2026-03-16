"""
GeoConvert - JPEG2000 image conversion via GDAL
"""

__version__ = "1.0.0"
__author__ = "GeoConvert"

from .core import ImageConverter
from .formats import SUPPORTED_FORMATS

__all__ = ["ImageConverter", "SUPPORTED_FORMATS"]
