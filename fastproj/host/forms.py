from django import forms
from .models import Client
from .models import Message
from .models import UploadClients

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['username', 'email', 'phoneNumber', 'rentPayDate', 'rentEndDate']

class GuestLoginForm(forms.Form):
    email = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content', 'file']
        

class UploadForm(forms.ModelForm):
    class Meta:
        model = UploadClients
        fields = ['description', 'file']
        