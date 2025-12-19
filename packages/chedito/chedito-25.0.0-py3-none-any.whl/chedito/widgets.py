"""
Chedito form widgets.

Provides RichTextWidget for rendering Quill.js editor in forms.
"""

import json

from django import forms
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string

from chedito.conf import chedito_settings


class RichTextWidget(forms.Textarea):
    """
    A Textarea widget that renders as a Quill.js rich text editor.

    Usage:
        class ArticleForm(forms.Form):
            content = forms.CharField(widget=RichTextWidget())

            # With custom configuration:
            content = forms.CharField(widget=RichTextWidget(
                quill_config={
                    'modules': {
                        'toolbar': ['bold', 'italic']
                    }
                }
            ))
    """

    template_name = "chedito/widget.html"

    def __init__(self, quill_config=None, attrs=None):
        """
        Initialize RichTextWidget.

        Args:
            quill_config: Custom Quill.js configuration to override defaults.
            attrs: HTML attributes for the widget container.
        """
        self.quill_config = quill_config or {}
        default_attrs = {
            "class": "chedito-widget",
            "rows": 10,
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)

    def get_quill_config(self):
        """Get the merged Quill.js configuration."""
        return chedito_settings.get_quill_config(self.quill_config)

    def get_context(self, name, value, attrs):
        """Build the context for rendering the widget template."""
        context = super().get_context(name, value, attrs)

        # Generate unique ID for this widget instance
        widget_id = attrs.get("id", name)
        editor_id = f"{widget_id}_editor"

        # Build Quill configuration
        quill_config = self.get_quill_config()

        context["widget"].update({
            "editor_id": editor_id,
            "quill_config": json.dumps(quill_config),
            "widget_height": chedito_settings.widget_height,
            "widget_min_height": chedito_settings.widget_min_height,
            "widget_max_height": chedito_settings.widget_max_height,
            "upload_image_url": "/chedito/upload/image/",
            "upload_video_url": "/chedito/upload/video/",
            "upload_file_url": "/chedito/upload/file/",
        })

        return context

    def render(self, name, value, attrs=None, renderer=None):
        """Render the widget as HTML."""
        if attrs is None:
            attrs = {}

        # Ensure we have an ID
        if "id" not in attrs:
            attrs["id"] = name

        context = self.get_context(name, value, attrs)
        return mark_safe(render_to_string(self.template_name, context))

    @property
    def media(self):
        """Return the CSS and JavaScript files needed for this widget."""
        return forms.Media(
            css={
                "all": [
                    "chedito/css/quill.snow.css",
                    "chedito/css/quill.bubble.css",
                    "chedito/css/chedito.css",
                ]
            },
            js=[
                "chedito/js/quill.min.js",
                "chedito/js/chedito.js",
            ]
        )


class AdminRichTextWidget(RichTextWidget):
    """
    RichTextWidget optimized for Django Admin.

    Includes additional styling for admin integration.
    """

    def __init__(self, quill_config=None, attrs=None):
        default_attrs = {
            "class": "chedito-widget chedito-admin-widget vLargeTextField",
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(quill_config=quill_config, attrs=default_attrs)

    @property
    def media(self):
        """Include admin-specific CSS."""
        base_media = super().media
        return base_media + forms.Media(
            css={
                "all": ["chedito/css/chedito-admin.css"]
            }
        )
