# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from forum.actions import UserJoinsAction
from forum.models.user import User
from forum.views.auth import login_and_forward


def create_user(request, *args, **kwargs):

    response = kwargs.get('response', {})
    details = kwargs.get('details', {})

    # User-specific information
    user_email = details.get('email')

    # Obtain or create user
    created = False
    try:
        user = User.objects.get(username=user_email)
    except User.DoesNotExist:
        created = True
        user = User(username=user_email)
        user.type = request.session['user_type']
        user.email = user_email
        user.first_name = details.get('first_name')
        user.last_name = details.get('last_name')
        user.set_unusable_password()

    facebook_access_token = response.get('access_token')
    facebook_uid = kwargs.get('uid')
    if facebook_access_token and facebook_uid:
        user.facebook_access_token = facebook_access_token
        user.facebook_uid = facebook_uid

    user.save()

    if created:
        UserJoinsAction(user=user, ip=request.META['REMOTE_ADDR']).save()

    return login_and_forward(request, user, reverse('homepage'), _("You are now logged in."))
