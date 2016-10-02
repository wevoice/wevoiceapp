from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe


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
            username = User.objects.get(username=self.cleaned_data['username'])
        except User.DoesNotExist:
            raise forms.ValidationError(self.fields['username'].error_messages['invalid'])
        return self.cleaned_data['username']

    def clean_password(self):
        cleaned_data = super(LoginForm, self).clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")
        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                pass
            else:
                raise forms.ValidationError(self.fields['password'].error_messages['incorrect'])


class SelectionForm(forms.Form):
    client_id = forms.IntegerField(required=True, widget=forms.HiddenInput())
    talent_id = forms.IntegerField(required=True, widget=forms.HiddenInput())


class HorizontalRadioRenderer(forms.RadioSelect.renderer):
    def render(self):
        return mark_safe(u'\n'.join([u'%s\n' % w for w in self]))


class CommentForm(forms.Form):
    CHOICES = (
        ("1", 1),
        ("2", 2),
        ("3", 3),
        ("4", 4),
        ("5", 5)
    )

    text = forms.CharField(
        required=False,
        max_length=512,
        widget=forms.TextInput(attrs={'class': "inputboxes03"})
    )
    client_id = forms.IntegerField(required=True, widget=forms.HiddenInput())
    selection_id=forms.IntegerField(required=True, widget=forms.HiddenInput())
    rating = forms.ChoiceField(
        required=False,
        choices=CHOICES,
        widget=forms.RadioSelect(renderer=HorizontalRadioRenderer))


class DeleteCommentForm(forms.Form):
    comment_id = forms.IntegerField(required=True, widget=forms.HiddenInput())
    client_id = forms.IntegerField(required=True, widget=forms.HiddenInput())
    selection_id=forms.IntegerField(required=True, widget=forms.HiddenInput())


