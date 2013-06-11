# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from forum.actions import UserJoinsAction
from forum.models.user import User
from forum.views.auth import login_and_forward


def create_user(request, *args, **kwargs):

    response = kwargs.get('response', {})
    details = kwargs.get('details', {})

    # Facebook information
    print response
    facebook_uid = kwargs.get('uid')
    facebook_email = details.get('email')
    facebook_access_token = response.get('access_token')

    changed = created = False

    try:
        user = User.objects.get(facebook_uid=facebook_uid)
    except User.DoesNotExist:
        try:
            user = User.objects.get(username=facebook_email)
        except User.DoesNotExist:
            if request.user.is_authenticated():
                user = request.user
            else:
                # Create user
                changed = created = True

                user = User(username=facebook_email, email=facebook_email)

                user.type = request.session['user_type']
                user.first_name = details.get('first_name')
                user.last_name = details.get('last_name')
                user.set_unusable_password()

    if facebook_access_token and facebook_uid:
        changed = True

        # Update Facebook information
        user.facebook_uid = facebook_uid
        user.facebook_email = facebook_email
        user.facebook_access_token = facebook_access_token

    if changed:
        user.save()

    if created:
        UserJoinsAction(user=user, ip=request.META['REMOTE_ADDR']).save()

    return login_and_forward(request, user, reverse('homepage'), _("You are now logged in."))
