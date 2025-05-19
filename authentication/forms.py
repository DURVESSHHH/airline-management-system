from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser
from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import datetime, timedelta

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'phone_number', 'country', 'city', 'address']  # Removed 'role'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'Customer'  # Set default role to Customer
        if commit:
            user.save()
        return user

class CustomAuthenticationForm(AuthenticationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'password']

from django import forms

class TwoFactorVerificationForm(forms.Form):
    code = forms.CharField(max_length=6, widget=forms.TextInput(attrs={'placeholder': 'Enter 6-digit code'}))

