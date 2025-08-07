"""Core app config."""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Core app config."""

    verbose_name = "Core"
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"
