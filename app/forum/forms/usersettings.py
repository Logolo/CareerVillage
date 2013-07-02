from general import NextUrlField,  UserNameField,  UserEmailField, SetPasswordForm
from forum.models import Question, User
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe
from django import forms
from django.core.exceptions import ValidationError
import logging


class SettingsAccountForm(forms.Form):
    #username = UserNameField()
    #realname = forms.CharField(label=_('Real name'), required=True, max_length=255, widget=forms.TextInput(attrs={'size' : 35, 'placeholder' : 'Placeholder for user\'s name'}))
    first_name = forms.CharField(label=_('First name'))
    last_name = forms.CharField(label=_('Last name'))
    #email = UserEmailField()
    email = forms.EmailField(label=_('Email'))

    def set_current_user(self, user):
        """ Set the user that is going to use the form.
        """
        self.current_user = user

    def clean_email(self):
        email = self.cleaned_data['email']

        current_user = getattr(self, 'current_user', None)
        users = User.objects.filter(email__iexact=email)
        if current_user:
            users = users.exclude(id=current_user.id)

        if users:
            raise ValidationError(_('This email is taken.'))
        else:
            return email

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

