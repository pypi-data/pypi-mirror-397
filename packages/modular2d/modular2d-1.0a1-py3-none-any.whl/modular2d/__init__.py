"""
__init__.py

This is the package initializer for the table formatting library.

It defines the version, imports main modules and classes,
and exposes a clean public API via __all__.
"""

# Package version
__version__ = "1.0.a"

# Import the main formatter module
from . import modulate
from .modulate import ListFormatter

# Import the border module and main Border class
from . import border
from .border import Border

# Import predefined border styles
from .border import BORDER_ASCII
from .border import BORDER_ASCII_LONG
from .border import ALL

# Define the public API of the package
__all__ = [
    "modulate",          # Main formatting module
    "ListFormatter",     # Primary class for table formatting
    "border",            # Module defining borders
    "Border",            # Border class
    "BORDER_ASCII",      # Default ASCII border
    "BORDER_ASCII_LONG", # Long dash border
    "ALL"                # List of all available borders
]