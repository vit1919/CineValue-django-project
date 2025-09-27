
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "password1", "password2")
        widgets = {
            "username":  forms.TextInput(attrs={
                "class": "form-control bg-dark text-light border-secondary"
            }),
            "password1": forms.PasswordInput(attrs={
                "class": "form-control bg-dark text-light border-secondary"
            }),
            "password2": forms.PasswordInput(attrs={
                "class": "form-control bg-dark text-light border-secondary"
            }),
        }
