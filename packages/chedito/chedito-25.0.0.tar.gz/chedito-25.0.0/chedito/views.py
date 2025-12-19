"""
Chedito upload views.

Handles file uploads for images, videos, and attachments.
"""

import json

from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.core.exceptions import PermissionDenied

from chedito.conf import chedito_settings
from chedito.utils import validate_file_type, validate_file_size


class BaseUploadView(View):
    """Base class for all upload views."""

    upload_type = "file"
    allowed_types_setting = "allowed_file_types"
    max_size_setting = "max_file_size"

    @method_decorator(csrf_protect)
    def dispatch(self, request, *args, **kwargs):
        """Handle request with CSRF protection."""
        return super().dispatch(request, *args, **kwargs)

    def check_permissions(self, request):
        """
        Check if the user has permission to upload.

        Raises PermissionDenied if not authorized.
        """
        if chedito_settings.require_authentication:
            if not request.user.is_authenticated:
                raise PermissionDenied("Authentication required for uploads.")

        if chedito_settings.staff_only_uploads:
            if not request.user.is_staff:
                raise PermissionDenied("Staff access required for uploads.")

    def get_allowed_types(self):
        """Get the list of allowed MIME types for this upload type."""
        return getattr(chedito_settings, self.allowed_types_setting)

    def get_max_size(self):
        """Get the maximum file size for this upload type."""
        return getattr(chedito_settings, self.max_size_setting)

    def post(self, request):
        """Handle file upload POST request."""
        try:
            self.check_permissions(request)
        except PermissionDenied as e:
            return JsonResponse({"error": str(e)}, status=403)

        if "file" not in request.FILES:
            return JsonResponse({"error": "No file provided."}, status=400)

        uploaded_file = request.FILES["file"]

        # Validate file type
        allowed_types = self.get_allowed_types()
        is_valid, error = validate_file_type(uploaded_file, allowed_types)
        if not is_valid:
            return JsonResponse({"error": error}, status=400)

        # Validate file size
        max_size = self.get_max_size()
        is_valid, error = validate_file_size(uploaded_file, max_size)
        if not is_valid:
            return JsonResponse({"error": error}, status=400)

        # Save the file
        try:
            storage = chedito_settings.get_storage()
            url = storage.save(uploaded_file, uploaded_file.name, self.upload_type)

            return JsonResponse({
                "success": True,
                "url": url,
                "filename": uploaded_file.name,
            })

        except Exception as e:
            return JsonResponse({
                "error": f"Failed to save file: {str(e)}"
            }, status=500)


class ImageUploadView(BaseUploadView):
    """Handle image uploads."""

    upload_type = "image"
    allowed_types_setting = "allowed_image_types"
    max_size_setting = "max_image_size"


class VideoUploadView(BaseUploadView):
    """Handle video uploads."""

    upload_type = "video"
    allowed_types_setting = "allowed_video_types"
    max_size_setting = "max_video_size"


class FileUploadView(BaseUploadView):
    """Handle generic file uploads (attachments)."""

    upload_type = "file"
    allowed_types_setting = "allowed_file_types"
    max_size_setting = "max_file_size"


# Function-based views for backwards compatibility
def upload_image(request):
    """Function-based view for image uploads."""
    return ImageUploadView.as_view()(request)


def upload_video(request):
    """Function-based view for video uploads."""
    return VideoUploadView.as_view()(request)


def upload_file(request):
    """Function-based view for file uploads."""
    return FileUploadView.as_view()(request)
