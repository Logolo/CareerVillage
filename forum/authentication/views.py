from django.shortcuts import redirect

from social_auth.views import complete as socialauth_complete, disconnect as socialauth_disconnect
from social_auth.exceptions import AuthAlreadyAssociated, NotAllowedToDisconnect


def complete(request, *args, **kwargs):
    """ Associate social account with user.
    """
    try:
        socialauth_complete(request, *args, **kwargs)
    except AuthAlreadyAssociated:
        # The social account is already associated to another user
        # TODO: Notify the user
        return redirect('homepage')

    return redirect('settings_social_networks')


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
    if user and user.is_authenticated() and user.has_usable_password():
        # Remove stored Facebook information
        if kwargs.get('backend') == 'facebook':
            user.facebook_access_token = ''
            user.facebook_uid = ''
            user.save()

    return redirect('settings_social_networks')
