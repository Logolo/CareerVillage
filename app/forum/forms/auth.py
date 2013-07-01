from django.forms.util import ErrorList
from general import NextUrlField,  UserNameField,  UserEmailField, SetPasswordForm
from forum.models import Question, User, Tag
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe
from django import forms
from django.db.models import Q
from django.core.exceptions import ValidationError
import logging


class SimpleRegistrationForm(forms.Form):
    next = NextUrlField()
    username = UserNameField()
    email = UserEmailField()


class ReviseProfileForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.none(), 
        widget=forms.CheckboxSelectMultiple, 
        required=False)

    def __init__(self, *args, **kwargs):
        super(ReviseProfileForm, self).__init__(*args, **kwargs)
        if args and args[0] and 'tags' in args[0]:
            self.fields['tags'].queryset = Tag.objects.filter(id__in=args[0].getlist('tags'))
        elif self.instance:
            selected_tags = Tag.objects.filter(marked_by=self.instance, user_selections__reason='good')
            self.fields['tags'].queryset = selected_tags
            self.fields['tags'].initial = selected_tags

        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'industry', 'headline', 'location', 'email')


class TemporaryLoginRequestForm(forms.Form):
    def __init__(self, data=None):
        super(TemporaryLoginRequestForm, self).__init__(data)
        self.user_cache = None

    email = forms.EmailField(
            required=True,
            label=_("Your account email"),
            error_messages={
                'required': _("You cannot leave this field blank"),
                'invalid': _('please enter a valid email address'),
            }
    )

    def clean_email(self):
        users = list(User.objects.filter(email=self.cleaned_data['email']))

        if not len(users):
            raise forms.ValidationError(_("Sorry, but this email is not on our database."))

        self.user_cache = users
        return self.cleaned_data['email']

class ChangePasswordForm(SetPasswordForm):
    """ change password form """
    oldpw = forms.CharField(widget=forms.PasswordInput(attrs={'class':'required'}),
                label=mark_safe(_('Current password')))

    def __init__(self, data=None, user=None, *args, **kwargs):
        if user is None:
            raise TypeError("Keyword argument 'user' must be supplied")
        super(ChangePasswordForm, self).__init__(data, *args, **kwargs)
        self.user = user

    def clean_oldpw(self):
        """ test old password """
        if not self.user.check_password(self.cleaned_data['oldpw']):
            raise forms.ValidationError(_("Old password is incorrect. \
                    Please enter the correct password."))
        return self.cleaned_data['oldpw']


class SignupForm(forms.ModelForm):

    email = forms.EmailField(label=_("Your email address"))
    password = forms.CharField(max_length=128, widget=forms.PasswordInput(), label=_("Create a password"))
    password_confirm = forms.CharField(max_length=128, widget=forms.PasswordInput, label=_("Confirm your password"))
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    avatar_image = forms.CharField(max_length=200)
    grade = forms.CharField(required=False)

    class Meta:
        model = User
        fields = ('email', 'password', 'first_name', 'last_name', 'location',)

    def available_avatars(self):
        return ["pixel_geek_%s_%s.png" % (g, e) for g in ['f', 'm'] for e in ['africa_carib', 'asian', 'black', 'blond', 'hispanic', 'red']]

    def available_grades(self):
        return [str(i) + "th" for i in range(5, 13)] + ['college', 'other']

    def clean_email(self):
        """ Validate email.
        """
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(Q(username=email) | Q(email=email)):
            raise ValidationError('That user already exists.')
        return email

    def is_valid(self):
        is_valid = super(SignupForm, self).is_valid()
        if is_valid:
            valid_grade = True
            valid_avatar = True
            valid_password = True
            if self.cleaned_data.get('grade') and not self.cleaned_data.get('grade') in self.available_grades():
                valid_grade = False
                self._errors['grade'].append("Invalid grade")
            if not self.cleaned_data['avatar_image'] in self.available_avatars():
                valid_avatar = False
                self._errors['avatar'].append("Invalid avatar")
            if self.cleaned_data['password'] != self.cleaned_data['password_confirm']:
                valid_password = False
                errors = self._errors.setdefault("password", ErrorList())
                errors.append(_("Passwords don't match"))
            return valid_grade and valid_avatar and valid_password
        else:
            return False

