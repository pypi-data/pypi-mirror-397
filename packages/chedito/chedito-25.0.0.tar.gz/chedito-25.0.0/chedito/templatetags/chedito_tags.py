"""
Chedito template tags.

Provides template tags for rendering rich text content and including assets.
"""

from django import template
from django.utils.safestring import mark_safe

from chedito.utils import sanitize_html
from chedito.conf import chedito_settings

register = template.Library()


@register.simple_tag
def render_rich_text(content, sanitize=True):
    """
    Render rich text content safely.

    Usage:
        {% load chedito_tags %}
        {% render_rich_text article.content %}

        {# Without sanitization (use with caution) #}
        {% render_rich_text article.content sanitize=False %}

    Args:
        content: The HTML content to render.
        sanitize: Whether to sanitize the HTML (default: True).

    Returns:
        Safe HTML string.
    """
    if not content:
        return ""

    if sanitize:
        content = sanitize_html(content)

    return mark_safe(content)


@register.simple_tag
def chedito_css():
    """
    Include Chedito CSS files.

    Usage:
        {% load chedito_tags %}
        <head>
            {% chedito_css %}
        </head>

    Returns:
        HTML link tags for CSS files.
    """
    from django.templatetags.static import static

    theme = chedito_settings.quill_theme

    tags = []

    # Add Quill theme CSS (bundled locally)
    if theme == "bubble":
        tags.append(f'<link rel="stylesheet" href="{static("chedito/css/quill.bubble.css")}">')
    else:
        tags.append(f'<link rel="stylesheet" href="{static("chedito/css/quill.snow.css")}">')

    # Add chedito custom CSS
    tags.append(f'<link rel="stylesheet" href="{static("chedito/css/chedito.css")}">')

    return mark_safe('\n'.join(tags))


@register.simple_tag
def chedito_js():
    """
    Include Chedito JavaScript files.

    Usage:
        {% load chedito_tags %}
        <body>
            ...
            {% chedito_js %}
        </body>

    Returns:
        HTML script tags for JavaScript files.
    """
    from django.templatetags.static import static

    tags = [
        f'<script src="{static("chedito/js/quill.min.js")}"></script>',
        f'<script src="{static("chedito/js/chedito.js")}"></script>',
    ]

    return mark_safe('\n'.join(tags))


@register.simple_tag
def chedito_assets():
    """
    Include all Chedito assets (CSS and JS).

    Usage:
        {% load chedito_tags %}
        <head>
            {% chedito_assets %}
        </head>

    Note: It's generally better to put CSS in <head> and JS before </body>,
    so prefer using chedito_css and chedito_js separately.

    Returns:
        HTML tags for all CSS and JS files.
    """
    css = chedito_css()
    js = chedito_js()
    return mark_safe(f'{css}\n{js}')


@register.inclusion_tag('chedito/widget.html')
def chedito_editor(name, value='', config=None, **attrs):
    """
    Render a standalone Chedito editor.

    Usage:
        {% load chedito_tags %}
        {% chedito_editor "content" article.content %}

        {# With custom configuration #}
        {% chedito_editor "content" article.content config=custom_config %}

    Args:
        name: The form field name.
        value: Initial value (HTML content).
        config: Optional Quill configuration dictionary.
        **attrs: Additional HTML attributes.

    Returns:
        Rendered editor HTML.
    """
    import json

    widget_id = attrs.get('id', name)
    editor_id = f'{widget_id}_editor'

    quill_config = chedito_settings.get_quill_config(config)

    return {
        'widget': {
            'name': name,
            'value': value,
            'attrs': {
                'id': widget_id,
                **attrs,
            },
            'editor_id': editor_id,
            'quill_config': json.dumps(quill_config),
            'widget_height': chedito_settings.widget_height,
            'widget_min_height': chedito_settings.widget_min_height,
            'widget_max_height': chedito_settings.widget_max_height,
            'upload_image_url': '/chedito/upload/image/',
            'upload_video_url': '/chedito/upload/video/',
            'upload_file_url': '/chedito/upload/file/',
        }
    }


@register.filter(name='richtext')
def richtext_filter(value, sanitize=True):
    """
    Filter to render rich text content.

    Usage:
        {% load chedito_tags %}
        {{ article.content|richtext }}

        {# Without sanitization #}
        {{ article.content|richtext:False }}

    Args:
        value: The HTML content to render.
        sanitize: Whether to sanitize (default: True).

    Returns:
        Safe HTML string.
    """
    if not value:
        return ""

    if sanitize:
        value = sanitize_html(value)

    return mark_safe(value)


@register.filter(name='strip_tags')
def strip_tags_filter(value):
    """
    Strip all HTML tags from content.

    Usage:
        {% load chedito_tags %}
        {{ article.content|strip_tags }}

    Args:
        value: The HTML content.

    Returns:
        Plain text string.
    """
    if not value:
        return ""

    import re
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', value)
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


@register.filter(name='truncate_richtext')
def truncate_richtext_filter(value, length=100):
    """
    Truncate rich text content to a specified length.

    Usage:
        {% load chedito_tags %}
        {{ article.content|truncate_richtext:200 }}

    Args:
        value: The HTML content.
        length: Maximum character length.

    Returns:
        Truncated plain text string with ellipsis.
    """
    if not value:
        return ""

    # Strip tags first
    text = strip_tags_filter(value)

    if len(text) <= length:
        return text

    # Find a good break point
    truncated = text[:length]
    last_space = truncated.rfind(' ')
    if last_space > length * 0.8:  # If space is reasonably close to end
        truncated = truncated[:last_space]

    return truncated + '...'
