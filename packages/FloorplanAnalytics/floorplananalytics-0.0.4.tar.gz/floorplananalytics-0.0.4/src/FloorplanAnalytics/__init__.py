"""FloorplanAnalytics - A library to analyze floor plans with common space syntax metrics."""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("FloorplanAnalytics")
except PackageNotFoundError:
    __version__ = "0.0.0-dev"  # Fallback for local development

from .analytics import *
from .lib.helper.Colorhelper import *
from .lib.helper.Helperfunctions import *

