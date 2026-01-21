"""
Custom template tags for media file handling
"""
from django import template
from django.conf import settings

register = template.Library()


@register.filter
def local_media_url(file_field):
    """
    Returns a local media URL for a file field.
    This is used when files are stored locally but the storage backend
    is configured for Supabase (which would return Supabase URLs).
    
    Usage: {{ record.document_file|local_media_url }}
    """
    if not file_field:
        return ''
    
    # Get the file name/path from the field
    if hasattr(file_field, 'name') and file_field.name:
        # Return local media URL
        return f"{settings.MEDIA_URL}{file_field.name}"
    
    return ''


@register.simple_tag
def media_url(file_field):
    """
    Returns the appropriate media URL for a file field.
    Prefers local URL over storage backend URL.
    
    Usage: {% media_url record.document_file %}
    """
    if not file_field:
        return ''
    
    if hasattr(file_field, 'name') and file_field.name:
        return f"{settings.MEDIA_URL}{file_field.name}"
    
    return ''
