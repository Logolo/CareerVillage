# -*- coding: utf-8 -*-
import datetime
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.utils.timezone import now
from forum.actions import UserJoinsAction
from forum.models import User, Tag, MarkedTag
from forum.views.auth import login_and_forward
from forum.authentication.backend import OverrideFacebookBackend, OverrideLinkedinOAuth2Backend
from forum import settings


FACEBOOK_APP = settings.djsettings.FACEBOOK_APP
LINKEDIN_APP = settings.djsettings.LINKEDIN_APP


def create_user(request, backend, uid=None, details={}, response={}, user=None, **kwargs):
    created = False
    linkedin_changed = False
    facebook_changed = False
    tags = []

    if user:
        user = User.objects.get(id=user.id)

    if backend.name == OverrideLinkedinOAuth2Backend.name:
        # 1. Extract data
        force_revise = False
        linkedin_uid = uid
        linkedin_email = details.get('email')
        linkedin_email_lower = linkedin_email.lower()
        linkedin_access_token = response.get('access_token')
        linkedin_photo_url = response.get('picture-url', '')

        # 2. Find user
        if not user:
            try:
                user = User.objects.get(linkedin_accounts__app=LINKEDIN_APP,
                                        linkedin_accounts__uid=linkedin_uid)
            except User.DoesNotExist:
                try:
                    user = User.objects.get(username=linkedin_email_lower)
                    force_revise = not user.linkedin_access_token
                except User.DoesNotExist:
                    if request.user.is_authenticated():
                        user = request.user
                    else:
                        # Create user
                        created = True
                        user = User(username=linkedin_email_lower, email=linkedin_email)
                        user.type = request.session['user_type']
                        user.first_name = details.get('first_name')
                        user.last_name = details.get('last_name')
                        user.set_unusable_password()
                        user.industry = response.get('industry', '')
                        user.headline = response.get('headline', '')
                        user.location = response.get('location', {}).get('name', '')
                        tags = [response.get('industry', '')]
                        tags.extend(s['skill']['name'].strip() for s in response.get('skills', {}).get('skill', []))
                        tags.extend(s.strip() for s in response.get('interests', '').split(','))

        # 3. Update social account
        linkedin_account = user.linkedin_account
        if created and linkedin_photo_url:
            linkedin_changed = True
            linkedin_account.photo_url = linkedin_photo_url
        if linkedin_access_token and linkedin_uid:
            linkedin_changed = True
            linkedin_account.uid = linkedin_uid
            linkedin_account.email = linkedin_email
            linkedin_account.access_token = linkedin_access_token
            linkedin_account.access_token_expires_on = now() + datetime.timedelta(days=58)

        # 4. Set next url
        if created or force_revise:
            next_url = request.POST.get('next', reverse('revise_profile'))
        else:
            next_url = request.POST.get('next', reverse('homepage'))

    elif backend.name == OverrideFacebookBackend.name:
        # 1. Extract data
        facebook_uid = uid
        facebook_email = details.get('email')
        facebook_email_lower = facebook_email.lower()
        facebook_access_token = response.get('access_token')

        # 2. Find user
        if not user:
            try:
                user = User.objects.get(facebook_accounts__app=FACEBOOK_APP,
                                        facebook_accounts__uid=facebook_uid)
            except User.DoesNotExist:
                try:
                    user = User.objects.get(username=facebook_email_lower)
                except User.DoesNotExist:
                    if request.user.is_authenticated():
                        user = request.user
                    else:
                        # Create user
                        created = True
                        user = User(username=facebook_email_lower, email=facebook_email)
                        user.type = request.session['user_type']
                        user.first_name = details.get('first_name')
                        user.last_name = details.get('last_name')
                        user.set_unusable_password()

        # 3. Update social account
        facebook_account = user.facebook_account
        if facebook_access_token and facebook_uid:
            facebook_changed = True
            facebook_account.uid = facebook_uid
            facebook_account.email = facebook_email
            facebook_account.access_token = facebook_access_token
            facebook_account.access_token_expires_on = now() + datetime.timedelta(days=58)

        # 4. Set next url
        next_url = request.POST.get('next', reverse('homepage'))

    if created:
        user.save()

    if linkedin_changed:
        if not linkedin_account.user_id:
            linkedin_account.user_id = user.id
        linkedin_account.save()

    if facebook_changed:
        if not facebook_account.user_id:
            facebook_account.user_id = user.id
        facebook_account.save()

    for tag in tags:
        if tag == '':
            continue
        try:
            tag = Tag.objects.get(name__iexact=Tag.make_name(tag))
        except Tag.DoesNotExist:
            tag = Tag.objects.create(name=tag, created_by=user)
        MarkedTag.objects.create(user=user, tag=tag, reason='good')

    return {
        'user': user,
        'next_url': next_url,
        'is_new': created
    }


def login(request, user, is_new=True, next_url=None, **kwargs):
    if is_new:
        UserJoinsAction(user=user, ip=request.META['REMOTE_ADDR']).save()
    return login_and_forward(request, user, next_url or reverse('homepage'), _("You are now logged in."))