# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from forum.actions import UserJoinsAction
from forum.models.user import User
from forum.views.auth import login_and_forward


def create_user(request, *args, **kwargs):
    backend = kwargs['backend']
    try:
        user = User.objects.get(username='%s:%s' % (backend.name, kwargs['uid'],))
    except User.DoesNotExist:
        user = User(username='%s:%s' % (backend.name, kwargs['uid'],))
        user.set_unusable_password()
        user.save()

        UserJoinsAction(user=user, ip=request.META['REMOTE_ADDR']).save()

    access_token = kwargs['response']['access_token']

    user.user_type = request.session['user_type']
    user.facebook_access_token = access_token
    user_details = kwargs.get('details', {})
    user.email = user_details.get('email')
    user.first_name = user_details.get('first_name', '')
    user.last_name = user_details.get('last_name', '')
    user.save()

    return login_and_forward(request, user, reverse('homepage'),
              _("You are now logged in.")
    )
