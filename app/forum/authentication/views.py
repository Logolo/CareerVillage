from django.shortcuts import redirect

from social_auth.views import complete as socialauth_complete, disconnect as socialauth_disconnect
from social_auth.exceptions import AuthAlreadyAssociated, NotAllowedToDisconnect, AuthCanceled


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
        if backend == 'facebook' and user.can_disconnect_facebook:
            user.facebook_uid = None
            user.facebook_email = None
            user.facebook_access_token = None
            user.facebook_access_token_expires_on = None
            user.save()

        # Remove stored LinkedIn information
        elif backend == 'linkedin-oauth2' and user.can_disconnect_linkedin:
            user.linkedin_uid = None
            user.linkedin_email = None
            user.linkedin_access_token = None
            user.linkedin_access_token_expires_on = None
            user.save()

    return redirect('settings_social_networks')
