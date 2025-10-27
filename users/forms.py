from django import forms
from .models import User

class UserRoleForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "username", "email", "first_name", "last_name", "role", "sub_role", "profile_photo"
        ]

class UserDeactivateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["is_active"]
