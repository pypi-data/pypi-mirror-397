"""
Chedito model fields.

Provides RichTextField for use in Django models.
"""

from django.db import models

from chedito.forms import RichTextFormField
from chedito.widgets import RichTextWidget


class RichTextField(models.TextField):
    """
    A TextField that renders as a rich text editor in forms.

    Usage:
        class Article(models.Model):
            content = RichTextField()

            # With custom configuration:
            content = RichTextField(
                quill_config={
                    'modules': {
                        'toolbar': ['bold', 'italic', 'link']
                    }
                }
            )
    """

    def __init__(self, *args, quill_config=None, widget_attrs=None, **kwargs):
        """
        Initialize RichTextField.

        Args:
            quill_config: Custom Quill.js configuration to override defaults.
            widget_attrs: Additional HTML attributes for the widget.
            *args, **kwargs: Standard TextField arguments.
        """
        self.quill_config = quill_config or {}
        self.widget_attrs = widget_attrs or {}
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        """Return arguments needed to reconstruct the field."""
        name, path, args, kwargs = super().deconstruct()
        if self.quill_config:
            kwargs["quill_config"] = self.quill_config
        if self.widget_attrs:
            kwargs["widget_attrs"] = self.widget_attrs
        return name, path, args, kwargs

    def formfield(self, **kwargs):
        """Return the form field for this model field."""
        widget = RichTextWidget(
            quill_config=self.quill_config,
            attrs=self.widget_attrs,
        )
        defaults = {
            "form_class": RichTextFormField,
            "widget": widget,
        }
        defaults.update(kwargs)
        return super().formfield(**defaults)

    def contribute_to_class(self, cls, name):
        """
        Hook called when field is added to a model class.

        Adds a helper method to get sanitized content.
        """
        super().contribute_to_class(cls, name)

        # Add a method to get sanitized content
        def get_sanitized_content(model_instance):
            from chedito.utils import sanitize_html
            value = getattr(model_instance, name)
            return sanitize_html(value) if value else ""

        setattr(cls, f"get_{name}_sanitized", get_sanitized_content)
