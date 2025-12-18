# dynamite/__init__.py

__version__ = "0.0.0"
__author__ = "laelume"

from .dynamo import main as dynamite
from . import ridge

__all__ = ["dynamite", "ridge"]