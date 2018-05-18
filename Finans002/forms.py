from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(max_length=30, label='')
    password = forms.CharField(max_length=50, widget=forms.PasswordInput, label='')
