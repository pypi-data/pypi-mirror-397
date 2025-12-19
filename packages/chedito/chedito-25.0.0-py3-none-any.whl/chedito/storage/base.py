"""
Chedito base storage backend.

Defines the interface for all storage backends.
"""

from abc import ABC, abstractmethod


class BaseStorage(ABC):
    """
    Abstract base class for Chedito storage backends.

    All storage backends must implement these methods.
    """

    @abstractmethod
    def save(self, file, filename):
        """
        Save a file and return its URL.

        Args:
            file: File-like object to save.
            filename: Desired filename (may be modified for uniqueness).

        Returns:
            URL string where the file can be accessed.
        """
        pass

    @abstractmethod
    def delete(self, filename):
        """
        Delete a file from storage.

        Args:
            filename: Name/path of the file to delete.

        Returns:
            True if deletion was successful, False otherwise.
        """
        pass

    @abstractmethod
    def url(self, filename):
        """
        Get the URL for accessing a file.

        Args:
            filename: Name/path of the file.

        Returns:
            URL string for accessing the file.
        """
        pass

    @abstractmethod
    def exists(self, filename):
        """
        Check if a file exists in storage.

        Args:
            filename: Name/path of the file to check.

        Returns:
            True if the file exists, False otherwise.
        """
        pass

    def get_available_name(self, filename):
        """
        Get an available filename, avoiding overwrites.

        Args:
            filename: Desired filename.

        Returns:
            Available filename string.
        """
        from chedito.utils import generate_unique_filename
        return generate_unique_filename(filename)
