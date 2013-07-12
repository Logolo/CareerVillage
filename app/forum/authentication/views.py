from django.shortcuts import redirect

from social_auth.views import complete as socialauth_complete, disconnect as socialauth_disconnect
from social_auth.exceptions import AuthAlreadyAssociated, NotAllowedToDisconnect, AuthCanceled
from forum.authentication.backend import OverrideFacebookBackend, OverrideLinkedinOAuth2Backend


def complete(request, *args, **kwargs):
    """ Associate social account with user.
    """
    try:
        return socialauth_complete(request, *args, **kwargs)
    except AuthAlreadyAssociated:
        # The social account is already associated to another user
        # TODO: Notify the user
        return redirect('homepage')
    except AuthCanceled:
        # The user canceled the process
        return redirect('homepage')


def disconnect(request, *args, **kwargs):
    """ Disconnect from social account.
    """
    try:
        socialauth_disconnect(request, *args, **kwargs)
    except NotAllowedToDisconnect:
        # The currently associated social account is the only way the user can sign in
        # TODO: Notify the user
        return redirect('homepage')

    user = request.user
    if user and user.is_authenticated():
        backend = kwargs.get('backend')

        # Remove stored Facebook information
        if backend == OverrideFacebookBackend.name and user.can_disconnect_facebook:
            user.facebook_account.delete()

        # Remove stored LinkedIn information
        elif backend == OverrideLinkedinOAuth2Backend.name and user.can_disconnect_linkedin:
            user.linkedin_account.delete()

    return redirect('settings_social_networks')
