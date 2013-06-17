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


class SocialSettingsForm(forms.Form):

    # Stories
    like_question_story = forms.BooleanField(initial=False, required=False)
    like_answer_story = forms.BooleanField(initial=False, required=False)
    ask_question_story = forms.BooleanField(initial=False, required=False)
    answer_question_story = forms.BooleanField(initial=False, required=False)
    award_badge_story = forms.BooleanField(initial=False, required=False)
    interest_topic_story = forms.BooleanField(initial=False, required=False)
    get_point_story = forms.BooleanField(initial=False, required=False)
    reach_point_story = forms.BooleanField(initial=False, required=False)

    # Notifications
    answer_question_notification = forms.BooleanField(initial=False, required=False)
    topic_question_notification = forms.BooleanField(initial=False, required=False)
    award_badge_notification = forms.BooleanField(initial=False, required=False)


# class SettingsPasswordForm(forms.Form):
#     currentpassword = forms.P
#     realname = forms.CharField(label=_('Real name'), required=True, max_length=255, widget=forms.TextInput(attrs={'size' : 35, 'placeholder' : 'Placeholder for user\'s name'}))
#     email = UserEmailField()

