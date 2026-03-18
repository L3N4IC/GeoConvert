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
Utilities: validation, logging, helpers.
"""

import os
import logging
from pathlib import Path
from typing import Optional

from .formats import SUPPORTED_INPUT_EXTENSIONS


def setup_logger(name: str = "geoconvert", level: int = logging.INFO) -> logging.Logger:
    """Configures a logger with colored formatting."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(level)
    return logger


def validate_input_file(filepath: str) -> Path:
    """
    Validates that the source file exists and is in a supported format.
    Returns a Path object if valid, raises ValueError otherwise.
    """
    path = Path(filepath)
    if not path.exists():
        raise ValueError(f"File not found: {filepath}")
    if not path.is_file():
        raise ValueError(f"This path is not a file: {filepath}")
    if path.suffix.lower() not in SUPPORTED_INPUT_EXTENSIONS:
        raise ValueError(
            f"Extension '{path.suffix}' not supported.\n"
            f"Supported input formats: {', '.join(SUPPORTED_INPUT_EXTENSIONS)}"
        )
    return path


def validate_output_dir(dirpath: str) -> Path:
    """Creates the output directory if it doesn't exist."""
    path = Path(dirpath)
    path.mkdir(parents=True, exist_ok=True)
    return path


def build_output_path(src: Path, output_dir: Optional[str], extension: str, suffix: str = "") -> Path:
    """
    Constructs the output file path.
    If output_dir is None, uses the same directory as the source.
    """
    stem = src.stem + suffix
    if output_dir:
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        return out_dir / (stem + extension)
    return src.parent / (stem + extension)


def get_human_size(size_bytes: int) -> str:
    """Formats a size in bytes into a human-readable string."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if abs(size_bytes) < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def collect_input_files(source: str) -> list[Path]:
    """
    Collects raster files from a file or a directory.
    Returns a list of valid Paths.
    """
    src = Path(source)
    files = []

    if src.is_file():
        validate_input_file(str(src))
        files.append(src)
    elif src.is_dir():
        for ext in SUPPORTED_INPUT_EXTENSIONS:
            files.extend(src.glob(f"*{ext}"))
            files.extend(src.glob(f"*{ext.upper()}"))
        files = sorted(set(files))
    else:
        raise ValueError(f"Invalid source: {source}")

    if not files:
        raise ValueError(f"No supported raster files found in: {source}")

    return files
