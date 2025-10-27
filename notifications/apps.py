from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "notifications"
    
    def ready(self):
        # Import signal handlers to wire up notifications
        try:
            # Import the module defining the handler function
            from . import signals as _signals
            # Connect the lecture attendance handler to the LectureAttendance model lazily
            from django.apps import apps as django_apps
            from django.db.models.signals import post_save

            LectureAttendance = django_apps.get_model('classes', 'LectureAttendance')
            if LectureAttendance is not None:
                post_save.connect(_signals.lecture_attendance_notification, sender=LectureAttendance)
        except Exception:
            # Avoid import errors during certain management commands
            pass
