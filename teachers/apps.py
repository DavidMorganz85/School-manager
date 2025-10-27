from django.apps import AppConfig


class TeachersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "teachers"

    def ready(self):
        # Import signal handlers
        try:
            import teachers.signals  # noqa: F401
        except Exception:
            pass
