from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from .models import UserActivity


@receiver(user_logged_in)
def log_login(sender, request, user, **kwargs):
    ip = request.META.get('REMOTE_ADDR')
    UserActivity.objects.create(user=user, action='login', ip_address=ip)


@receiver(user_logged_out)
def log_logout(sender, request, user, **kwargs):
    ip = request.META.get('REMOTE_ADDR')
    if user is not None:
        UserActivity.objects.create(user=user, action='logout', ip_address=ip)
