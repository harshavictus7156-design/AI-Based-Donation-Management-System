from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "notifications"

    def ready(self):
        # Register model-status hooks after Django has loaded all apps.
        from . import signals  # noqa: F401
