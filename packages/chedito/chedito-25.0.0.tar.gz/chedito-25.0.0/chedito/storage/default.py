"""
Chedito default storage backend.

Uses Django's default_storage for file operations.
"""

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from chedito.storage.base import BaseStorage
from chedito.conf import chedito_settings
from chedito.utils import generate_unique_filename


class DefaultStorage(BaseStorage):
    """
    Storage backend that uses Django's default storage.

    This allows chedito to automatically use whatever storage backend
    is configured in Django settings (local, S3, GCS, etc.).
    """

    def __init__(self):
        self.storage = default_storage
        self.upload_path = chedito_settings.upload_path

    def _get_path(self, filename, upload_type="file"):
        """Generate the full storage path for a file."""
        base = self.upload_path.rstrip("/")
        return f"{base}/{upload_type}s/{filename}"

    def save(self, file, filename, upload_type="file"):
        """
        Save a file using Django's default storage.

        Args:
            file: File-like object or UploadedFile.
            filename: Original filename.
            upload_type: Type of upload ("image", "video", "file").

        Returns:
            URL where the file can be accessed.
        """
        # Generate unique filename
        unique_filename = generate_unique_filename(filename)
        path = self._get_path(unique_filename, upload_type)

        # Handle different file types
        if hasattr(file, "read"):
            content = file.read()
            if hasattr(file, "seek"):
                file.seek(0)
        else:
            content = file

        # Save the file
        saved_path = self.storage.save(path, ContentFile(content))

        return self.url(saved_path)

    def delete(self, filename):
        """
        Delete a file from Django's default storage.

        Args:
            filename: Path of the file to delete.

        Returns:
            True if deletion was successful, False otherwise.
        """
        try:
            if self.storage.exists(filename):
                self.storage.delete(filename)
                return True
            return False
        except Exception:
            return False

    def url(self, filename):
        """
        Get the URL for a file.

        Args:
            filename: Path of the file.

        Returns:
            URL string for accessing the file.
        """
        return self.storage.url(filename)

    def exists(self, filename):
        """
        Check if a file exists.

        Args:
            filename: Path of the file to check.

        Returns:
            True if the file exists, False otherwise.
        """
        return self.storage.exists(filename)
