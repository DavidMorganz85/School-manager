from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    ROLE_CHOICES = [
        ("admin", "Admin"),
        ("headteacher", "Headteacher/Principal"),
        ("deputy_headteacher", "Deputy Headteacher"),
        ("director_of_studies", "Director of Studies"),
        ("hod", "Head of Department"),
        ("teacher", "Teacher"),
        ("student", "Student"),
        ("non_teaching", "Non-Teaching Staff"),
    ]
    NON_TEACHING_SUBROLE_CHOICES = [
        ("accounts", "Accounts Office"),
        ("welfare", "Welfare Officer"),
        ("cleaner", "Cleaner/Support Staff"),
        ("it_support", "IT Support"),
    ]
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default="student")
    sub_role = models.CharField(max_length=30, choices=NON_TEACHING_SUBROLE_CHOICES, null=True, blank=True)
    # Contact & profile
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    profile_photo = models.ImageField(upload_to="profiles/", null=True, blank=True)
    # Approval & timestamps
    is_approved = models.BooleanField(default=False)
    # During migrations we provide a default to allow adding this field to existing DBs.
    # created_at uses a plain default so migrations can set a value for existing rows.
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class UserActivity(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    action = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - {self.action} @ {self.created_at.isoformat()}"
# users app models (custom user will be implemented here)
