from django.contrib.auth.backends import ModelBackend
from forum.models import User
from forum import settings

from social_auth.backends.facebook import FacebookBackend, FacebookAuth
from social_auth.backends.contrib.linkedin import LinkedinOAuth2Backend, LinkedinOAuth2


class OverrideFacebookBackend(FacebookBackend):
    name = getattr(settings.djsettings, 'FACEBOOK_OVERRIDE_BACKEND_NAME',
                   FacebookBackend.name)


class OverrideFacebookAuth(FacebookAuth):
    AUTH_BACKEND = OverrideFacebookBackend


class OverrideLinkedinOAuth2Backend(LinkedinOAuth2Backend):
    name = getattr(settings.djsettings, 'LINKEDIN_OVERRIDE_BACKEND_NAME',
                   LinkedinOAuth2Backend.name)


class OverrideLinkedinOAuth2(LinkedinOAuth2):
    AUTH_BACKEND = OverrideLinkedinOAuth2Backend


BACKENDS = {
    OverrideFacebookBackend.name: OverrideFacebookAuth,
    OverrideLinkedinOAuth2Backend.name: OverrideLinkedinOAuth2,
}


class CaseInsensitiveModelBackend(ModelBackend):
    """
    By default ModelBackend does case _sensitive_ username authentication, which isn't what is
    generally expected.  This backend supports case insensitive username authentication.
    """
    def authenticate(self, username=None, password=None):
        try:
            user = User.objects.get(username__iexact=username)
            if user.check_password(password):
                return user
            else:
                return None
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None