# -*- coding: utf-8 -*-
import datetime
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.utils.timezone import now
from forum.actions import UserJoinsAction
from forum.models import User, Tag, MarkedTag
from forum.views.auth import login_and_forward


def create_user(request, *args, **kwargs):

    backend = kwargs['backend'].name
    response = kwargs.get('response', {})
    details = kwargs.get('details', {})

    changed = created = False
    tags = []

    if backend == 'linkedin':
        force_revise = False

        linkedin_uid = kwargs.get('uid')
        linkedin_email = details.get('email')
        linkedin_email_lower = linkedin_email.lower()
        linkedin_access_token = response.get('access_token')

        try:
            user = User.objects.get(linkedin_uid=linkedin_uid)
        except User.DoesNotExist:
            try:
                user = User.objects.get(username=linkedin_email_lower)
                if not user.linkedin_access_token:
                    force_revise = True
            except User.DoesNotExist:
                if request.user.is_authenticated():
                    user = request.user
                else:
                    # Create user
                    changed = created = True
                    user = User(username=linkedin_email_lower, email=linkedin_email)
                    user.type = request.session['user_type']
                    user.first_name = details.get('first_name')
                    user.last_name = details.get('last_name')
                    user.set_unusable_password()

                    if User.objects.all().count() == 0:
                        user.is_superuser = True
                        user.is_staff = True

                    user.industry = response.get('industry', '')
                    user.headline = response.get('headline', '')
                    user.location = response.get('location', {}).get('name', '')
                    user.linkedin_photo_url = response.get('picture-url', '')
                    tags = [response.get('industry', '')]
                    tags.extend(s['skill']['name'].strip() for s in response.get('skills', {}).get('skill', []))
                    tags.extend(s.strip() for s in response.get('interests', '').split(','))

        if linkedin_access_token and linkedin_uid:
            changed = True
            user.linkedin_uid = linkedin_uid
            user.linkedin_email = linkedin_email
            user.linkedin_access_token = linkedin_access_token
            user.linkedin_access_token_expires_on = now() + datetime.timedelta(days=58)

        if created or force_revise:
            next_url = request.POST.get('next', reverse('revise_profile'))
        else:
            next_url = request.POST.get('next', reverse('homepage'))

    elif backend == 'facebook':
        facebook_uid = kwargs.get('uid')
        facebook_email = details.get('email')
        facebook_email_lower = facebook_email.lower()
        facebook_access_token = response.get('access_token')

        try:
            user = User.objects.get(facebook_uid=facebook_uid)
        except User.DoesNotExist:
            try:
                user = User.objects.get(username=facebook_email_lower)
            except User.DoesNotExist:
                if request.user.is_authenticated():
                    user = request.user
                else:
                    # Create user
                    changed = created = True
                    user = User(username=facebook_email_lower, email=facebook_email)
                    user.type = request.session['user_type']
                    user.first_name = details.get('first_name')
                    user.last_name = details.get('last_name')
                    user.set_unusable_password()

        if facebook_access_token and facebook_uid:
            changed = True
            user.facebook_uid = facebook_uid
            user.facebook_email = facebook_email
            user.facebook_access_token = facebook_access_token
            user.facebook_access_token_expires_on = now() + datetime.timedelta(days=58)

        next_url = request.POST.get('next', reverse('homepage'))

    if changed:
        user.save()

    for tag in tags:
        if tag == '':
            continue
        try:
            tag = Tag.objects.get(name__iexact=Tag.make_name(tag))
        except Tag.DoesNotExist:
            tag = Tag.objects.create(name=tag, created_by=user)
        MarkedTag.objects.create(user=user, tag=tag, reason='good')

    if created:
        UserJoinsAction(user=user, ip=request.META['REMOTE_ADDR']).save()

    return login_and_forward(request, user, next_url, _("You are now logged in."))
