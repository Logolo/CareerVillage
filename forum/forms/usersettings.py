from general import NextUrlField,  UserNameField,  UserEmailField, SetPasswordForm
from forum.models import Question, User
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe
from django import forms
import logging

class SettingsAccountForm(forms.Form):
    username = UserNameField()
    realname = forms.CharField(label=_('Real name'), required=True, max_length=255, widget=forms.TextInput(attrs={'size' : 35, 'placeholder' : 'Placeholder for user\'s name'}))
    email = UserEmailField()

# class SettingsPasswordForm(forms.Form):
#     currentpassword = forms.P
#     realname = forms.CharField(label=_('Real name'), required=True, max_length=255, widget=forms.TextInput(attrs={'size' : 35, 'placeholder' : 'Placeholder for user\'s name'}))
#     email = UserEmailField()

