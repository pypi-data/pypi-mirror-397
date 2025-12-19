"""
Chedito - A Django Rich Text Editor Package

A modern, feature-rich text editor for Django.
"""

__version__ = "25.0.0"
__author__ = "Emmanuel Asamoah"
__email__ = "emmanuelasamoah179@gmail.com"
__license__ = "MIT"

default_app_config = "chedito.apps.CheditoConfig"

from chedito.fields import RichTextField
from chedito.widgets import RichTextWidget
from chedito.forms import RichTextFormField

__all__ = [
    "RichTextField",
    "RichTextWidget",
    "RichTextFormField",
    "__version__",
]
