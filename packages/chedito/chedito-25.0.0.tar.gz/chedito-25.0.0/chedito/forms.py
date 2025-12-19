"""
Chedito form fields.

Provides RichTextFormField for use in Django forms.
"""

from django import forms
from django.core.exceptions import ValidationError

from chedito.utils import sanitize_html
from chedito.widgets import RichTextWidget
from chedito.conf import chedito_settings


class RichTextFormField(forms.CharField):
    """
    A CharField that uses RichTextWidget and provides HTML sanitization.

    Usage:
        class ArticleForm(forms.Form):
            content = RichTextFormField()

            # With custom configuration:
            content = RichTextFormField(
                quill_config={'theme': 'bubble'},
                sanitize=True,
                max_length=50000,
            )
    """

    widget = RichTextWidget

    def __init__(
        self,
        *args,
        quill_config=None,
        sanitize=None,
        allowed_tags=None,
        allowed_attributes=None,
        **kwargs
    ):
        """
        Initialize RichTextFormField.

        Args:
            quill_config: Custom Quill.js configuration.
            sanitize: Whether to sanitize HTML (default from settings).
            allowed_tags: List of allowed HTML tags.
            allowed_attributes: Dict of allowed attributes per tag.
            *args, **kwargs: Standard CharField arguments.
        """
        self.quill_config = quill_config or {}
        self.sanitize = sanitize if sanitize is not None else chedito_settings.sanitize_html
        self.allowed_tags = allowed_tags
        self.allowed_attributes = allowed_attributes

        # Create widget with config
        if "widget" not in kwargs:
            kwargs["widget"] = RichTextWidget(quill_config=self.quill_config)

        super().__init__(*args, **kwargs)

    def clean(self, value):
        """
        Validate and clean the submitted value.

        Performs HTML sanitization if enabled.
        """
        value = super().clean(value)

        if value and self.sanitize:
            value = sanitize_html(
                value,
                allowed_tags=self.allowed_tags,
                allowed_attributes=self.allowed_attributes,
            )

        return value

    def has_changed(self, initial, data):
        """Check if the field value has changed."""
        # Normalize both values for comparison
        if initial is None:
            initial = ""
        if data is None:
            data = ""

        # Strip whitespace and empty paragraph tags for comparison
        initial_normalized = self._normalize_html(initial)
        data_normalized = self._normalize_html(data)

        return initial_normalized != data_normalized

    def _normalize_html(self, html):
        """Normalize HTML for comparison."""
        if not html:
            return ""

        # Remove empty paragraphs and excess whitespace
        import re
        html = re.sub(r"<p>\s*<br\s*/?>\s*</p>", "", html)
        html = re.sub(r"<p>\s*</p>", "", html)
        html = re.sub(r"\s+", " ", html)
        return html.strip()


class RichTextInlineFormField(RichTextFormField):
    """
    RichTextFormField optimized for inline forms in Django Admin.

    Uses a more compact configuration suitable for inline editing.
    """

    def __init__(self, *args, **kwargs):
        # Use a simpler toolbar for inline forms
        if "quill_config" not in kwargs:
            kwargs["quill_config"] = {
                "modules": {
                    "toolbar": [
                        ["bold", "italic", "underline"],
                        ["link", "image"],
                        [{"list": "ordered"}, {"list": "bullet"}],
                        ["clean"],
                    ]
                }
            }
        super().__init__(*args, **kwargs)
