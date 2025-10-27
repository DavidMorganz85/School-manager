from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "users"

    def ready(self):
        # import signal handlers
        try:
            import users.signals  # noqa: F401
        except Exception:
            pass
