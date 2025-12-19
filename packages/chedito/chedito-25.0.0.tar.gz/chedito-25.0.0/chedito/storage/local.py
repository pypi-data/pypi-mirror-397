"""
Chedito local filesystem storage backend.

Stores files directly on the local filesystem.
"""

import os
import shutil

from django.conf import settings

from chedito.storage.base import BaseStorage
from chedito.conf import chedito_settings
from chedito.utils import generate_unique_filename


class LocalStorage(BaseStorage):
    """
    Storage backend that saves files to the local filesystem.

    Files are stored within MEDIA_ROOT and served via MEDIA_URL.
    """

    def __init__(self, location=None, base_url=None):
        """
        Initialize LocalStorage.

        Args:
            location: Base directory for file storage (default: MEDIA_ROOT).
            base_url: Base URL for serving files (default: MEDIA_URL).
        """
        self.location = location or getattr(settings, "MEDIA_ROOT", "")
        self.base_url = base_url or getattr(settings, "MEDIA_URL", "/media/")
        self.upload_path = chedito_settings.upload_path

        if not self.location:
            raise ValueError(
                "LocalStorage requires MEDIA_ROOT to be configured in Django settings."
            )

    def _get_path(self, filename, upload_type="file"):
        """Generate the full filesystem path for a file."""
        base = self.upload_path.rstrip("/")
        return os.path.join(self.location, base, f"{upload_type}s", filename)

    def _get_relative_path(self, filename, upload_type="file"):
        """Generate the relative path (for URL generation)."""
        base = self.upload_path.rstrip("/")
        return f"{base}/{upload_type}s/{filename}"

    def _ensure_directory(self, filepath):
        """Ensure the directory for a file exists."""
        directory = os.path.dirname(filepath)
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

    def save(self, file, filename, upload_type="file"):
        """
        Save a file to the local filesystem.

        Args:
            file: File-like object or UploadedFile.
            filename: Original filename.
            upload_type: Type of upload ("image", "video", "file").

        Returns:
            URL where the file can be accessed.
        """
        # Generate unique filename
        unique_filename = generate_unique_filename(filename)
        filepath = self._get_path(unique_filename, upload_type)

        # Ensure directory exists
        self._ensure_directory(filepath)

        # Write the file
        if hasattr(file, "chunks"):
            # Django UploadedFile
            with open(filepath, "wb") as dest:
                for chunk in file.chunks():
                    dest.write(chunk)
        elif hasattr(file, "read"):
            # File-like object
            with open(filepath, "wb") as dest:
                shutil.copyfileobj(file, dest)
        else:
            # Raw bytes
            with open(filepath, "wb") as dest:
                dest.write(file)

        relative_path = self._get_relative_path(unique_filename, upload_type)
        return self.url(relative_path)

    def delete(self, filename):
        """
        Delete a file from the local filesystem.

        Args:
            filename: Relative path of the file to delete.

        Returns:
            True if deletion was successful, False otherwise.
        """
        filepath = os.path.join(self.location, filename)

        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                return True
            return False
        except Exception:
            return False

    def url(self, filename):
        """
        Get the URL for a file.

        Args:
            filename: Relative path of the file.

        Returns:
            URL string for accessing the file.
        """
        base_url = self.base_url.rstrip("/")
        filename = filename.lstrip("/")
        return f"{base_url}/{filename}"

    def exists(self, filename):
        """
        Check if a file exists.

        Args:
            filename: Relative path of the file to check.

        Returns:
            True if the file exists, False otherwise.
        """
        filepath = os.path.join(self.location, filename)
        return os.path.exists(filepath)
