"""
Chedito configuration management.

Provides a centralized way to access chedito settings with defaults.
"""

from django.conf import settings
from django.utils.module_loading import import_string


# Default configuration
DEFAULTS = {
    # Upload settings
    "upload_path": "chedito_uploads/",
    "storage_backend": "chedito.storage.default.DefaultStorage",

    # File type restrictions
    "allowed_image_types": [
        "image/jpeg",
        "image/png",
        "image/gif",
        "image/webp",
        "image/svg+xml",
    ],
    "allowed_video_types": [
        "video/mp4",
        "video/webm",
        "video/ogg",
    ],
    "allowed_file_types": [
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/zip",
        "text/plain",
        "text/csv",
    ],

    # Size limits (in bytes)
    "max_image_size": 5 * 1024 * 1024,  # 5MB
    "max_video_size": 50 * 1024 * 1024,  # 50MB
    "max_file_size": 10 * 1024 * 1024,  # 10MB

    # Security
    "require_authentication": False,
    "staff_only_uploads": False,

    # HTML sanitization
    "sanitize_html": True,
    "allowed_tags": [
        "p", "br", "strong", "em", "u", "s", "sub", "sup",
        "h1", "h2", "h3", "h4", "h5", "h6",
        "ul", "ol", "li",
        "blockquote", "pre", "code",
        "a", "img", "video", "source", "iframe",
        "table", "thead", "tbody", "tr", "th", "td",
        "span", "div",
    ],
    "allowed_attributes": {
        "*": ["class", "style"],
        "a": ["href", "title", "target", "rel"],
        "img": ["src", "alt", "title", "width", "height"],
        "video": ["src", "controls", "width", "height", "poster"],
        "source": ["src", "type"],
        "iframe": ["src", "width", "height", "frameborder", "allowfullscreen"],
        "td": ["colspan", "rowspan"],
        "th": ["colspan", "rowspan"],
    },
    "allowed_styles": [
        "color", "background-color", "font-size", "font-family",
        "text-align", "text-decoration", "font-weight", "font-style",
    ],

    # Quill configuration
    "quill_theme": "snow",  # "snow" or "bubble"
    "quill_config": {
        "modules": {
            "toolbar": [
                [{"header": [1, 2, 3, 4, 5, 6, False]}],
                ["bold", "italic", "underline", "strike"],
                [{"color": []}, {"background": []}],
                [{"script": "sub"}, {"script": "super"}],
                ["blockquote", "code-block"],
                [{"list": "ordered"}, {"list": "bullet"}],
                [{"indent": "-1"}, {"indent": "+1"}],
                [{"direction": "rtl"}],
                [{"align": []}],
                ["link", "image", "video"],
                ["clean"],
            ],
            "clipboard": {
                "matchVisual": False,
            },
        },
        "placeholder": "Write something...",
    },

    # Widget settings
    "widget_height": "300px",
    "widget_min_height": "150px",
    "widget_max_height": None,
}


class CheditoSettings:
    """
    Settings object for Chedito.

    Allows attribute-style access to settings with fallback to defaults.
    """

    def __init__(self):
        self._cached_settings = None

    @property
    def user_settings(self):
        """Get user-defined settings from Django settings."""
        if self._cached_settings is None:
            self._cached_settings = getattr(settings, "CHEDITO_CONFIG", {})
        return self._cached_settings

    def __getattr__(self, name):
        """Get a setting value, falling back to default."""
        if name.startswith("_"):
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

        if name in self.user_settings:
            return self.user_settings[name]

        if name in DEFAULTS:
            return DEFAULTS[name]

        raise AttributeError(f"Invalid chedito setting: '{name}'")

    def get(self, name, default=None):
        """Get a setting with optional default."""
        try:
            return getattr(self, name)
        except AttributeError:
            return default

    def get_storage_class(self):
        """Import and return the configured storage class."""
        return import_string(self.storage_backend)

    def get_storage(self):
        """Get an instance of the configured storage backend."""
        storage_class = self.get_storage_class()
        return storage_class()

    def get_quill_config(self, extra_config=None):
        """
        Get the Quill configuration dictionary.

        Args:
            extra_config: Additional configuration to merge.

        Returns:
            Complete Quill configuration dictionary.
        """
        config = {
            "theme": self.quill_theme,
            **self.quill_config,
        }

        if extra_config:
            config = self._deep_merge(config, extra_config)

        return config

    def _deep_merge(self, base, override):
        """Deep merge two dictionaries."""
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    def reload(self):
        """Clear cached settings, forcing a reload on next access."""
        self._cached_settings = None


# Global settings instance
chedito_settings = CheditoSettings()
