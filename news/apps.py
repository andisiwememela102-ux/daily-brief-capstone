"""Django application configuration for the newsroom app."""

from django.apps import AppConfig

class NewsConfig(AppConfig):
    """Configure the newsroom app and load its model signals."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'news'

    def ready(self):
        """Register signal handlers when Django starts the app."""
        from . import signals  # noqa: F401
