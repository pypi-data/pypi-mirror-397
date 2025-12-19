from django.apps import AppConfig


class CheditoConfig(AppConfig):
    """Django app configuration for Chedito."""

    name = "chedito"
    verbose_name = "Chedito Rich Text Editor"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        """Perform initialization when Django starts."""
        pass
