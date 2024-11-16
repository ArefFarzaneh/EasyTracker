from django.apps import AppConfig


class EasytrackerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "EasyTracker"

    def ready(self):
        import EasyTracker.signals
