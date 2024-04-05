# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    phone = forms.CharField(max_length=15)
    address = forms.CharField(max_length=100)
    eircode = forms.CharField(max_length=10)
    country = forms.CharField(max_length=50)

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'phone', 'address', 'eircode', 'country']
# Path: register/views.py