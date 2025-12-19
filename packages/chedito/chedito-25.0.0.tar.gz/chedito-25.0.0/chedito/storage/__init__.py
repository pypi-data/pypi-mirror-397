"""
Chedito storage backends.

Provides pluggable storage backends for handling file uploads.
"""

from chedito.storage.base import BaseStorage
from chedito.storage.default import DefaultStorage
from chedito.storage.local import LocalStorage

__all__ = [
    "BaseStorage",
    "DefaultStorage",
    "LocalStorage",
]
