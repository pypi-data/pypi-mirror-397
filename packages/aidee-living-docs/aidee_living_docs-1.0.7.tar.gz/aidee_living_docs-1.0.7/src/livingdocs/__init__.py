"""Initialize the livingdocs package."""

import importlib.metadata

from .json_formatter import JSONFormatter


__all__ = [
    "JSONFormatter",
]

try:
    __version__ = importlib.metadata.version("aidee-living-docs")
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.0.0"
