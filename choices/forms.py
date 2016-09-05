from django import forms
from models import Client
import hashlib


class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=254,
        widget=forms.TextInput(attrs={'class': "inputboxes01"}),
        error_messages={'invalid': 'A valid username is required'}
    )
    password = forms.CharField(
        max_length=254,
        widget=forms.TextInput(attrs={'class': "inputboxes01"}),
        error_messages={'incorrect': 'Password is incorrect'}
    )

    def clean_username(self):
        try:
            client = Client.objects.get(username=self.cleaned_data['username'])
        except Client.DoesNotExist:
            raise forms.ValidationError(self.fields['username'].error_messages['invalid'])
        return self.cleaned_data['username']

    def clean_password(self):
        cleaned_data = super(LoginForm, self).clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")
        client = None
        if username and password:
            # Only do something if both fields are valid so far.
            try:
                client = Client.objects.get(username=username)
            except Client.DoesNotExist:
                raise forms.ValidationError(self.fields['username'].error_messages['invalid'])
            if client.password != hashlib.md5(password.encode('utf-8')).hexdigest():
                raise forms.ValidationError(self.fields['password'].error_messages['incorrect'])

