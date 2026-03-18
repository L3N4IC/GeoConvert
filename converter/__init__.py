# Copyright 2026 HOUIZOT Lénaïc
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
GeoConvert - JPEG2000 image conversion via GDAL
"""

__version__ = "1.0.0"
__author__ = "GeoConvert"

from .core import ImageConverter
from .formats import SUPPORTED_FORMATS

__all__ = ["ImageConverter", "SUPPORTED_FORMATS"]
