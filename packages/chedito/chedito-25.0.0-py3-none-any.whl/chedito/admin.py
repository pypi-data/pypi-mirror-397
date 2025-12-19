"""
Chedito Django Admin integration.

Provides mixins and helpers for seamless admin integration.
"""

from django.contrib import admin
from django.db import models

from chedito.fields import RichTextField
from chedito.widgets import AdminRichTextWidget


class RichTextAdminMixin:
    """
    Mixin for ModelAdmin to automatically use RichTextWidget for RichTextField.

    Usage:
        @admin.register(Article)
        class ArticleAdmin(RichTextAdminMixin, admin.ModelAdmin):
            list_display = ['title', 'created']

    This mixin automatically:
    - Uses AdminRichTextWidget for all RichTextField fields
    - Includes necessary CSS/JS media files
    - Supports inline admins
    """

    # Custom configuration for rich text fields in admin
    chedito_config = None

    def get_form(self, request, obj=None, **kwargs):
        """Override form to use AdminRichTextWidget for RichTextField."""
        form = super().get_form(request, obj, **kwargs)
        return form

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        """Use AdminRichTextWidget for RichTextField fields."""
        if isinstance(db_field, RichTextField):
            widget_config = db_field.quill_config.copy() if db_field.quill_config else {}

            # Merge admin-level configuration
            if self.chedito_config:
                widget_config = self._merge_config(widget_config, self.chedito_config)

            kwargs['widget'] = AdminRichTextWidget(
                quill_config=widget_config,
                attrs=db_field.widget_attrs,
            )

        return super().formfield_for_dbfield(db_field, request, **kwargs)

    def _merge_config(self, base, override):
        """Deep merge two configuration dictionaries."""
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        return result

    @property
    def media(self):
        """Include Chedito media files."""
        base_media = super().media
        chedito_media = AdminRichTextWidget().media
        return base_media + chedito_media


class RichTextStackedInline(admin.StackedInline):
    """
    StackedInline with RichTextField support.

    Usage:
        class CommentInline(RichTextStackedInline):
            model = Comment
            extra = 1
    """

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        """Use AdminRichTextWidget for RichTextField fields."""
        if isinstance(db_field, RichTextField):
            # Use a more compact configuration for inlines
            inline_config = {
                'modules': {
                    'toolbar': [
                        ['bold', 'italic', 'underline'],
                        ['link', 'image'],
                        [{'list': 'ordered'}, {'list': 'bullet'}],
                        ['clean'],
                    ]
                }
            }

            if db_field.quill_config:
                inline_config = self._merge_config(inline_config, db_field.quill_config)

            kwargs['widget'] = AdminRichTextWidget(
                quill_config=inline_config,
                attrs={'class': 'chedito-inline-widget'},
            )

        return super().formfield_for_dbfield(db_field, request, **kwargs)

    def _merge_config(self, base, override):
        """Deep merge two configuration dictionaries."""
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        return result


class RichTextTabularInline(admin.TabularInline):
    """
    TabularInline with RichTextField support.

    Usage:
        class CommentInline(RichTextTabularInline):
            model = Comment
            extra = 1
    """

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        """Use AdminRichTextWidget for RichTextField fields."""
        if isinstance(db_field, RichTextField):
            # Use minimal configuration for tabular inlines
            inline_config = {
                'modules': {
                    'toolbar': [
                        ['bold', 'italic'],
                        ['link'],
                        ['clean'],
                    ]
                }
            }

            if db_field.quill_config:
                inline_config = self._merge_config(inline_config, db_field.quill_config)

            kwargs['widget'] = AdminRichTextWidget(
                quill_config=inline_config,
                attrs={'class': 'chedito-tabular-widget'},
            )

        return super().formfield_for_dbfield(db_field, request, **kwargs)

    def _merge_config(self, base, override):
        """Deep merge two configuration dictionaries."""
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        return result


def register_chedito_admin(model_class, admin_class=None):
    """
    Convenience function to register a model with RichTextAdminMixin.

    Usage:
        from chedito.admin import register_chedito_admin
        from .models import Article

        register_chedito_admin(Article)

        # Or with custom admin class:
        class ArticleAdmin(admin.ModelAdmin):
            list_display = ['title']

        register_chedito_admin(Article, ArticleAdmin)
    """
    if admin_class is None:
        admin_class = admin.ModelAdmin

    # Create new class with mixin
    new_admin_class = type(
        f'{model_class.__name__}Admin',
        (RichTextAdminMixin, admin_class),
        {}
    )

    admin.site.register(model_class, new_admin_class)
