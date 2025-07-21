from django import forms
from django.contrib.auth.forms import UserCreationForm
from core.models import User

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, max_length=200, widget=forms.EmailInput(attrs={'class': 'form-control', 'id':'floatingInput', 'placeholder':'Enter email'}))
    first_name = forms.CharField(max_length=250, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'id':'floatingInput', 'placeholder':'First Name'}))
    last_name = forms.CharField(max_length=250, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'id':'floatingInput', 'placeholder':'Last Name'}))
    password1 = forms.CharField(max_length=50, required=True, widget=forms.PasswordInput(attrs={'class': 'form-control', 'id':'floatingInput', 'placeholder':'Password'}))
    password2 = forms.CharField(max_length=50, required=True, widget=forms.PasswordInput(attrs={'class': 'form-control', 'id':'floatingInput', 'placeholder':'Confirm password'}))

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password1', 'password2')

class LoginForm(forms.Form):
    email = forms.EmailField(required=True, max_length=200, widget=forms.EmailInput(attrs={'class': 'form-control form-control-lg', 'id':'floatingInput', 'placeholder':'Email address'}))
    password = forms.CharField(max_length=50, required=True, widget=forms.PasswordInput(attrs={'class': 'form-control form-control-lg', 'id':'floatingInput', 'placeholder':'Password'}))