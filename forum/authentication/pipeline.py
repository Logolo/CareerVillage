# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from forum.actions import UserJoinsAction
from forum.models.user import User
from forum.views.auth import login_and_forward


def create_user(request, *args, **kwargs):
    backend = kwargs['backend']

    response = kwargs.get('response', {})
    details = kwargs.get('details', {})

    # User type
    user_type = request.session['user_type']

    # Facebook-specific information
    facebook_access_token = response.get('access_token')
    facebook_uid = kwargs.get('uid')

    # User-specific information
    user_email = details.get('email')
    user_first_name = details.get('first_name')
    user_last_name = details.get('last_name')

    # Obtain user
    try:
        user = User.objects.get(username=user_email)
    except User.DoesNotExist:
        # Create user
        user = User(username=user_email)
        user.set_unusable_password()
        user.save()

        # Register action
        UserJoinsAction(user=user, ip=request.META['REMOTE_ADDR']).save()

    # Update information
    user.user_type = user_type

    if facebook_access_token and facebook_uid:
        user.facebook_access_token = facebook_access_token
        user.facebook_uid = facebook_uid

    user.first_name = user_first_name
    user.last_name = user_last_name

    user.save()

    return login_and_forward(request, user, reverse('homepage'), _("You are now logged in."))
