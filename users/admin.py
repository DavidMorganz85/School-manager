from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(DefaultUserAdmin):
    fieldsets = DefaultUserAdmin.fieldsets + (("Role & profile", {"fields": ("role", "sub_role", "profile_photo")} ),)
    list_display = ("username", "email", "role", "sub_role", "is_active", "is_staff")
from django.contrib import admin

# register user-related models here
