# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [25.0.0] - 2025-12-18

### Added

- Initial release of Chedito
- Rich text editing with Quill.js
- `RichTextField` model field for Django models
- `RichTextWidget` form widget
- `RichTextFormField` form field
- Full Django Admin integration with `RichTextAdminMixin`
- Support for stacked and tabular inlines
- Image upload with drag & drop and paste support
- Video upload support
- File attachment support
- Multiple storage backends:
  - `DefaultStorage` - Uses Django's default storage
  - `LocalStorage` - Local filesystem storage
- HTML sanitization for XSS protection
- Configurable toolbar
- Snow and Bubble themes
- Template tags:
  - `{% render_rich_text %}`
  - `{% chedito_css %}`
  - `{% chedito_js %}`
  - `{% chedito_editor %}`
  - `|richtext` filter
  - `|strip_tags` filter
  - `|truncate_richtext` filter
- Comprehensive configuration options
- Full documentation

### Security

- Built-in HTML sanitization
- CSRF protection for uploads
- File type validation
- File size limits
- Configurable authentication requirements
