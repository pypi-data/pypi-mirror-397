"""
Chedito utility functions.

Provides helper functions for HTML sanitization, file validation, etc.
"""

import os
import re
import uuid
import mimetypes
from html.parser import HTMLParser
from urllib.parse import urlparse

from django.utils.text import slugify

from chedito.conf import chedito_settings


class HTMLSanitizer(HTMLParser):
    """
    A simple HTML sanitizer that removes disallowed tags and attributes.

    This is a basic implementation. For production use with user-generated content,
    consider using bleach or nh3 for more robust sanitization.
    """

    def __init__(self, allowed_tags=None, allowed_attributes=None, allowed_styles=None):
        super().__init__()
        self.allowed_tags = allowed_tags or chedito_settings.allowed_tags
        self.allowed_attributes = allowed_attributes or chedito_settings.allowed_attributes
        self.allowed_styles = allowed_styles or chedito_settings.allowed_styles
        self.result = []
        self.tag_stack = []

    def handle_starttag(self, tag, attrs):
        if tag in self.allowed_tags:
            filtered_attrs = self._filter_attributes(tag, attrs)
            attr_string = self._build_attr_string(filtered_attrs)
            self.result.append(f"<{tag}{attr_string}>")
            self.tag_stack.append(tag)

    def handle_endtag(self, tag):
        if tag in self.allowed_tags and self.tag_stack and self.tag_stack[-1] == tag:
            self.result.append(f"</{tag}>")
            self.tag_stack.pop()

    def handle_data(self, data):
        self.result.append(self._escape_html(data))

    def handle_entityref(self, name):
        self.result.append(f"&{name};")

    def handle_charref(self, name):
        self.result.append(f"&#{name};")

    def _filter_attributes(self, tag, attrs):
        """Filter attributes based on allowed list."""
        filtered = []
        global_allowed = self.allowed_attributes.get("*", [])
        tag_allowed = self.allowed_attributes.get(tag, [])
        allowed = set(global_allowed + tag_allowed)

        for name, value in attrs:
            if name in allowed:
                if name == "style":
                    value = self._filter_styles(value)
                elif name == "href":
                    value = self._sanitize_url(value)
                elif name == "src":
                    value = self._sanitize_url(value)
                if value is not None:
                    filtered.append((name, value))

        return filtered

    def _filter_styles(self, style_string):
        """Filter CSS styles based on allowed list."""
        if not style_string:
            return None

        allowed_styles = []
        for part in style_string.split(";"):
            part = part.strip()
            if ":" in part:
                prop, _ = part.split(":", 1)
                prop = prop.strip().lower()
                if prop in self.allowed_styles:
                    allowed_styles.append(part)

        return "; ".join(allowed_styles) if allowed_styles else None

    def _sanitize_url(self, url):
        """Sanitize URLs to prevent javascript: and data: schemes."""
        if not url:
            return None

        url = url.strip()
        parsed = urlparse(url)

        # Allow relative URLs and safe schemes
        safe_schemes = ("http", "https", "mailto", "tel", "")
        if parsed.scheme.lower() not in safe_schemes:
            return None

        return url

    def _build_attr_string(self, attrs):
        """Build HTML attribute string."""
        if not attrs:
            return ""

        parts = []
        for name, value in attrs:
            if value is None:
                parts.append(f" {name}")
            else:
                escaped_value = self._escape_attr(value)
                parts.append(f' {name}="{escaped_value}"')

        return "".join(parts)

    def _escape_html(self, text):
        """Escape HTML special characters in text content."""
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )

    def _escape_attr(self, value):
        """Escape HTML special characters in attribute values."""
        return (
            value.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )

    def get_result(self):
        """Get the sanitized HTML string."""
        return "".join(self.result)


def sanitize_html(html_content, allowed_tags=None, allowed_attributes=None, allowed_styles=None):
    """
    Sanitize HTML content by removing disallowed tags and attributes.

    Args:
        html_content: The HTML string to sanitize.
        allowed_tags: List of allowed tag names.
        allowed_attributes: Dict mapping tag names to allowed attributes.
        allowed_styles: List of allowed CSS property names.

    Returns:
        Sanitized HTML string.
    """
    if not html_content:
        return ""

    if not chedito_settings.sanitize_html:
        return html_content

    try:
        import nh3
        return nh3.clean(
            html_content,
            tags=set(allowed_tags or chedito_settings.allowed_tags),
            attributes=allowed_attributes or chedito_settings.allowed_attributes,
        )
    except ImportError:
        pass

    try:
        import bleach
        return bleach.clean(
            html_content,
            tags=allowed_tags or chedito_settings.allowed_tags,
            attributes=allowed_attributes or chedito_settings.allowed_attributes,
            strip=True,
        )
    except ImportError:
        pass

    # Fallback to our basic sanitizer
    sanitizer = HTMLSanitizer(allowed_tags, allowed_attributes, allowed_styles)
    sanitizer.feed(html_content)
    return sanitizer.get_result()


def validate_file_type(uploaded_file, allowed_types):
    """
    Validate that an uploaded file is of an allowed type.

    Args:
        uploaded_file: Django UploadedFile object.
        allowed_types: List of allowed MIME types.

    Returns:
        Tuple of (is_valid, error_message).
    """
    content_type = uploaded_file.content_type

    # Also check by extension as a fallback
    filename = uploaded_file.name
    guessed_type, _ = mimetypes.guess_type(filename)

    if content_type in allowed_types:
        return True, None

    if guessed_type and guessed_type in allowed_types:
        return True, None

    return False, f"File type '{content_type}' is not allowed. Allowed types: {', '.join(allowed_types)}"


def validate_file_size(uploaded_file, max_size):
    """
    Validate that an uploaded file doesn't exceed the size limit.

    Args:
        uploaded_file: Django UploadedFile object.
        max_size: Maximum size in bytes.

    Returns:
        Tuple of (is_valid, error_message).
    """
    if uploaded_file.size > max_size:
        max_mb = max_size / (1024 * 1024)
        file_mb = uploaded_file.size / (1024 * 1024)
        return False, f"File size ({file_mb:.2f}MB) exceeds maximum allowed ({max_mb:.2f}MB)"

    return True, None


def generate_unique_filename(original_filename):
    """
    Generate a unique filename while preserving the extension.

    Args:
        original_filename: Original filename string.

    Returns:
        Unique filename string.
    """
    name, ext = os.path.splitext(original_filename)
    # Slugify the name and add UUID
    safe_name = slugify(name)[:50]  # Limit length
    unique_id = uuid.uuid4().hex[:8]
    return f"{safe_name}_{unique_id}{ext.lower()}"


def sanitize_filename(filename):
    """
    Sanitize a filename to remove potentially dangerous characters.

    Args:
        filename: Original filename string.

    Returns:
        Sanitized filename string.
    """
    # Remove path components
    filename = os.path.basename(filename)

    # Remove null bytes
    filename = filename.replace("\x00", "")

    # Replace spaces with underscores
    filename = filename.replace(" ", "_")

    # Remove any characters that aren't alphanumeric, underscore, hyphen, or period
    filename = re.sub(r"[^\w\-.]", "", filename)

    # Ensure the filename isn't empty
    if not filename or filename.startswith("."):
        filename = f"file_{uuid.uuid4().hex[:8]}"

    return filename


def get_upload_path(instance, filename, upload_type="file"):
    """
    Generate upload path for a file.

    Args:
        instance: Model instance (can be None).
        filename: Original filename.
        upload_type: Type of upload ("image", "video", "file").

    Returns:
        Full upload path string.
    """
    base_path = chedito_settings.upload_path.rstrip("/")
    safe_filename = generate_unique_filename(filename)
    return f"{base_path}/{upload_type}s/{safe_filename}"
