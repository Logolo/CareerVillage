from django.contrib import messages
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from forum.models import User
from django.http import HttpResponseRedirect, Http404
from forum.http_responses import HttpResponseUnauthorized
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django.utils.http import urlquote_plus
from forum.views.decorators import login_required
from forum.modules import decorate
from django.contrib.auth import login, logout
from django.http import get_host
from forum.actions import SuspendAction
from forum.utils import html
from forum import settings
from writers import manage_pending_data
import types
import datetime
import logging

from forum.forms import SimpleRegistrationForm, ReviseProfileForm, TemporaryLoginRequestForm, \
        ChangePasswordForm, SetPasswordForm, StudentSignupForm
from forum.utils.mail import send_template_email

from forum.authentication.base import InvalidAuthentication
from forum.authentication import AUTH_PROVIDERS

from forum.models import AuthKeyUserAssociation, ValidationHash, Question, Answer, Tag, MarkedTag
from forum.actions import UserJoinsAction

from forum.settings import REP_GAIN_BY_EMAIL_VALIDATION
from vars import ON_SIGNIN_SESSION_ATTR, PENDING_SUBMISSION_SESSION_ATTR

def signin_page(request):
    referer = request.META.get('HTTP_REFERER', '/')

    # If the referer is equal to the sign up page, e. g. if the previous login attempt was not successful we do not
    # change the sign in URL. The user should go to the same page.
    if not referer.replace(settings.APP_URL, '') == reverse('auth_signin'):
        request.session[ON_SIGNIN_SESSION_ATTR] = referer

    all_providers = [provider.context for provider in AUTH_PROVIDERS.values() if provider.context]

    sort = lambda c1, c2: c1.weight - c2.weight
    can_show = lambda c: not request.user.is_authenticated() or c.show_to_logged_in_user

    bigicon_providers = sorted([
    context for context in all_providers if context.mode == 'BIGICON' and can_show(context)
    ], sort)

    smallicon_providers = sorted([
    context for context in all_providers if context.mode == 'SMALLICON' and can_show(context)
    ], sort)

    top_stackitem_providers = sorted([
    context for context in all_providers if context.mode == 'TOP_STACK_ITEM' and can_show(context)
    ], sort)

    stackitem_providers = sorted([
    context for context in all_providers if context.mode == 'STACK_ITEM' and can_show(context)
    ], sort)

    try:
        msg = request.session['auth_error']
        del request.session['auth_error']
    except:
        msg = None

    return render_to_response(
            'auth/signin.html',
            {
            'msg': msg,
            'all_providers': all_providers,
            'bigicon_providers': bigicon_providers,
            'top_stackitem_providers': top_stackitem_providers,
            'stackitem_providers': stackitem_providers,
            'smallicon_providers': smallicon_providers,
            },
            RequestContext(request))


def login_page(request):
    try:
        msg = request.session['auth_error']
        del request.session['auth_error']
    except:
        msg = None
    return render_to_response('v2/account_signin.html', {'msg': msg}, RequestContext(request))


def signup_student(request):
    if request.method == 'POST':
        form = StudentSignupForm(request.POST)
        if form.is_valid():
            user_ = User(username=form.cleaned_data['email'], email=form.cleaned_data['email'])
            user_.set_password(form.cleaned_data['password'])
            user_.first_name = form.cleaned_data['first_name']
            user_.last_name = form.cleaned_data['last_name']
            user_.save()

            if form.cleaned_data.get('location'):
                user_.location = form.cleaned_data['location']
            if form.cleaned_data.get('grade'):
                user_.grade = form.cleaned_data['grade']
            user_.avatar_image = form.cleaned_data['avatar_image']
            user_.user_type = 'student'

            if User.objects.all().count() == 0:
                user_.is_superuser = True
                user_.is_staff = True

            user_.save()

            UserJoinsAction(user=user_, ip=request.META['REMOTE_ADDR']).save()

            send_validation_email(request)
            redirect_to = request.GET.get('next', reverse('homepage'))

            return login_and_forward(request, user_, redirect_to,
                              _("A confirmation email has been sent to your inbox."))

        else:
            return render_to_response('v2/account_signup_student.html', {'form': form, 'data':form.is_valid()}, RequestContext(request))
    else:
        form = StudentSignupForm()
        return render_to_response('v2/account_signup_student.html', {'form': form}, RequestContext(request))


def prepare_provider_signin(request, provider):
    force_email_request = request.REQUEST.get('validate_email', 'yes') == 'yes'
    request.session['force_email_request'] = force_email_request

    if provider in AUTH_PROVIDERS:
        provider_class = AUTH_PROVIDERS[provider].consumer

        try:
            request_url = provider_class.prepare_authentication_request(request,
                                                                        reverse('auth_provider_done',
                                                                                kwargs={'provider': provider}))

            return HttpResponseRedirect(request_url)
        except NotImplementedError, e:
            return process_provider_signin(request, provider)
        except InvalidAuthentication, e:
            request.session['auth_error'] = e.message

        return HttpResponseRedirect(reverse('auth_signin'))
    else:
        raise Http404()


def process_provider_signin(request, provider):
    if provider in AUTH_PROVIDERS:
        provider_class = AUTH_PROVIDERS[provider].consumer

        try:
            assoc_key = provider_class.process_authentication_request(request)
        except InvalidAuthentication, e:
            request.session['auth_error'] = e.message
            return HttpResponseRedirect(reverse('auth_signin'))

        if request.user.is_authenticated():
            if isinstance(assoc_key, (type, User)):
                if request.user != assoc_key:
                    request.session['auth_error'] = _(
                            "Sorry, these login credentials belong to another user. Please terminate your current session (by logging out or clearing your cookies) and try again. For help, contact us at team@careervillage.org"
                            )
                else:
                    request.session['auth_error'] = _("You are already logged in with that user.")
            else:
                try:
                    assoc = AuthKeyUserAssociation.objects.get(key=assoc_key)
                    if assoc.user == request.user:
                        request.session['auth_error'] = _(
                                "These login credentials are already associated with your account.")
                    else:
                        request.session['auth_error'] = _(
                                "Sorry, these login credentials belong to another user. Please terminate your current session (by logging out or clearing your cookies) and try again. For help, contact us at team@careervillage.org"
                                )
                except:
                    uassoc = AuthKeyUserAssociation(user=request.user, key=assoc_key, provider=provider)
                    uassoc.save()
                    messages.success(request,
                            message=_('The new credentials are now associated with your account'))
                    return HttpResponseRedirect(reverse('user_authsettings', args=[request.user.id]))

            return HttpResponseRedirect(reverse('auth_signin'))
        else:
            if isinstance(assoc_key, User):
                return login_and_forward(request, assoc_key)

        try:
            assoc = AuthKeyUserAssociation.objects.get(key=assoc_key)
            user_ = assoc.user
            return login_and_forward(request, user_)
        except AuthKeyUserAssociation.DoesNotExist:
            user_ = _create_linkedin_user(request, assoc_key)
            if user_:
                return login_and_forward(request, user_, request.POST.get('next', reverse('revise_profile')))

    return HttpResponseRedirect(reverse('auth_signin'))


def _create_linkedin_user(request, assoc_key):

    provider_class = AUTH_PROVIDERS['linkedin'].consumer
    user_data = provider_class.get_user_data(request.session['oauth2_access_token'])
    user_ = User(username='linkedin:%s' % (user_data['id'],))
    user_.set_unusable_password()
    user_.save()

    if User.objects.all().count() == 0:
        user_.is_superuser = True
        user_.is_staff = True


    location = user_data.get('location', None)
    user_.first_name = user_data.get('firstName', '')
    user_.last_name = user_data.get('lastName', '')
    user_.email = user_data.get('emailAddress', '')
    user_.industry = user_data.get('industry', '')
    user_.headline = user_data.get('headline', '')
    user_.location = location.get('name', '') if location else ''
    user_.linkedin_photo_url = user_data.get('pictureUrl', '')
    tags = [user_data['industry']]
    if 'skills' in user_data:
        tags.extend(s['skill']['name'] for s in user_data['skills']['values'])
    if 'interests' in user_data:
        tags.extend(i.strip() for i in user_data['interests'].split(','))

    user_.save()

    for tag_name in tags:
        try:
            tag = Tag.objects.get(name=tag_name)
        except Tag.DoesNotExist:
            tag = Tag.objects.create(name=tag_name, created_by=user_)
        MarkedTag.objects.create(user=user_, tag=tag, reason='good')

    UserJoinsAction(user=user_, ip=request.META['REMOTE_ADDR']).save()

    uassoc = AuthKeyUserAssociation(user=user_, key=assoc_key, provider='linkedin')
    uassoc.save()

    request.session.pop('oauth2_access_token', None)

    return user_


def external_register(request):
    if request.method == 'POST' and 'bnewaccount' in request.POST:
        form1 = SimpleRegistrationForm(request.POST)

        if form1.is_valid():
            user_ = User(username=form1.cleaned_data['email'], email=form1.cleaned_data['email'])
            user_.email_isvalid = request.session.get('auth_validated_email', '') == form1.cleaned_data['email']
            user_.set_unusable_password()

            if User.objects.all().count() == 0:
                user_.is_superuser = True
                user_.is_staff = True

            forward = None
            auth_provider = request.session.get('auth_provider', None)
            tags = []
            if auth_provider == 'linkedin':
                provider_class = AUTH_PROVIDERS[auth_provider].consumer
                user_data = provider_class.get_user_data(request.session['oauth2_access_token'])
                location = user_data.get('location', None)
                user_.first_name = user_data.get('firstName','').strip()
                user_.last_name = user_data.get('lastName','').strip()
                user_.industry = user_data.get('industry', '')
                user_.headline = user_data.get('headline', '')
                user_.location = location.get('name', '') if location else ''
                user_.linkedin_photo_url = user_data.get('pictureUrl', '')
                tags = [user_data['industry']]          
                if 'skills' in user_data:      
                    tags.extend(s['skill']['name'] for s in user_data['skills']['values'])
                if 'interests' in user_data:
                    tags.extend(i.strip() for i in user_data['interests'].split(','))
                forward = reverse('revise_profile')

            user_.save()

            for tag_name in tags:
                try:
                    tag = Tag.objects.get(name=tag_name)
                except Tag.DoesNotExist:
                    tag = Tag.objects.create(name=tag_name, created_by=user_)
                MarkedTag.objects.create(user=user_, tag=tag, reason='good')                

            UserJoinsAction(user=user_, ip=request.META['REMOTE_ADDR']).save()

            try:
                assoc_key = request.session['assoc_key']
                auth_provider = request.session['auth_provider']
            except:
                request.session['auth_error'] = _(
                        "Oops, something went wrong in the middle of this process. Please try again. Note that you need to have cookies enabled for the authentication to work."
                        )
                logging.error("Missing session data when trying to complete user registration: %s" % ", ".join(
                        ["%s: %s" % (k, v) for k, v in request.META.items()]))
                return HttpResponseRedirect(reverse('auth_signin'))

            uassoc = AuthKeyUserAssociation(user=user_, key=assoc_key, provider=auth_provider)
            uassoc.save()

            del request.session['assoc_key']
            del request.session['auth_provider']
            request.session.pop('oauth2_access_token', None)

            return login_and_forward(request, user_, forward, message=_("A welcome email has been sent to your email address. "))
    else:
        auth_provider = request.session.get('auth_provider', None)
        if not auth_provider:
            request.session['auth_error'] = _(
                    "Oops, something went wrong in the middle of this process. Please try again.")
            logging.error("Missing session data when trying to complete user registration: %s" % ", ".join(
                    ["%s: %s" % (k, v) for k, v in request.META.items()]))
            return HttpResponseRedirect(reverse('auth_signin'))

        user_data = request.session.get('auth_consumer_data', {})

        username = user_data.get('username', '')
        email = user_data.get('email', '')

        if email:
            request.session['auth_validated_email'] = email

        form1 = SimpleRegistrationForm(initial={
        'next': '/',
        'username': username,
        'email': email,
        })

    provider_context = AUTH_PROVIDERS[request.session['auth_provider']].context

    return render_to_response('auth/complete.html', {
    'form1': form1,
    'provider':provider_context and mark_safe(provider_context.human_name) or _('unknown'),
    'login_type':provider_context.id,
    'gravatar_faq_url':reverse('faq') + '#gravatar',
    }, context_instance=RequestContext(request))

@decorate.withfn(login_required)
def revise_profile(request):
    form = ReviseProfileForm(request.POST or None, instance=request.user)
    if form.is_valid():        
        form.save()
        request.user.tag_selections.all().delete()
        for tag in form.cleaned_data['tags']:
            if not MarkedTag.objects.filter(user=request.user, tag=tag):
                MarkedTag.objects.create(user=request.user, tag=tag, reason='good')
        if 'new_tags' in request.POST:
            for tag_name in request.POST.getlist('new_tags'):
                tag_name = tag_name.strip()
                if tag_name:
                    try:
                        tag = Tag.objects.get(name=tag_name)
                    except Tag.DoesNotExist:
                        tag = Tag.objects.create(name=tag_name, created_by=request.user)
                    if not MarkedTag.objects.filter(user=request.user, tag=tag):
                        MarkedTag.objects.create(user=request.user, tag=tag, reason='good')
        return HttpResponseRedirect(reverse('homepage'))

    return render_to_response('v2/revise_profile.html', {
    'profile_form': form,
    }, context_instance=RequestContext(request))

def request_temp_login(request):
    if request.method == 'POST':
        form = TemporaryLoginRequestForm(request.POST)

        if form.is_valid():
            users = form.user_cache

            for u in users:
                if u.is_suspended():
                    return forward_suspended_user(request, u, False)

            for u in users:
                try:
                    hash = get_object_or_404(ValidationHash, user=u, type='templogin')
                    if hash.expiration < datetime.datetime.now():
                        hash.delete()
                        return request_temp_login(request)
                except:
                    hash = ValidationHash.objects.create_new(u, 'templogin', [u.id])

                send_template_email([u], "auth/temp_login_email.html", {'temp_login_code': hash})

                messages.info(request, message=_("An email will be sent with your temporary login key. Please allow up to three minutes for it to arrive and check your spam folder!"))

            return HttpResponseRedirect(reverse('homepage'))
    else:
        form = TemporaryLoginRequestForm()

    return render_to_response(
            'auth/temp_login_request.html', {'form': form},
            context_instance=RequestContext(request))

def request_temp_login_v2(request):
    if request.method == 'POST':
        form = TemporaryLoginRequestForm(request.POST)

        if form.is_valid():
            users = form.user_cache

            for u in users:
                if u.is_suspended():
                    return forward_suspended_user(request, u, False)

            for u in users:
                try:
                    hash = get_object_or_404(ValidationHash, user=u, type='templogin')
                    if hash.expiration < datetime.datetime.now():
                        hash.delete()
                        return request_temp_login(request)
                except:
                    hash = ValidationHash.objects.create_new(u, 'templogin', [u.id])

                send_template_email([u], "v2/emails/password-reset.html", {'temp_login_code': hash})

                messages.info(request, message=_("An email will be sent with your temporary login key. Please allow up to three minutes for it to arrive and check your spam folder!"))

            return HttpResponseRedirect(reverse('login'))
    else:
        form = TemporaryLoginRequestForm()

    return render_to_response(
            'v2/password_reset.html', {'form': form},
            context_instance=RequestContext(request))

def temp_signin(request, user, code):
    user = get_object_or_404(User, id=user)

    if (ValidationHash.objects.validate(code, user, 'templogin', [user.id])):
        
        # If the user requests temp_signin he must have forgotten his password. So we mark it as unusable.
        user.set_unusable_password()
        user.save()
        
        return login_and_forward(request, user, reverse('user_authsettings', kwargs={'id': user.id}),
                                 _(
                                         "You are logged in with a temporary access key, please take the time to fix your issue with authentication."
                                         ))
    else:
        raise Http404()

def send_validation_email(request):
    if not request.user.is_authenticated():
        return HttpResponseUnauthorized(request)
    else:
        # We check if there are some old validation hashes. If there are -- we delete them.
        try:
            hash = ValidationHash.objects.get(user=request.user, type='email')
            hash.delete()
        except:
            pass

        # We don't care if there are previous cashes in the database... In every case we have to create a new one
        hash = ValidationHash.objects.create_new(request.user, 'email', [request.user.email])

        send_template_email([request.user], "auth/mail_validation.html", {'validation_code': hash})
        messages.info(request, message=_("A message with an email validation link was just sent to your address."))
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

        

def validate_email(request, user, code):
    user = get_object_or_404(User, id=user)

    if (ValidationHash.objects.validate(code, user, 'email', [user.email])):
        user.email_isvalid = True
        user.save()
        return login_and_forward(request, user, reverse('homepage'), _("Thank you, your email is now validated."))
    else:
        return render_to_response('auth/mail_already_validated.html', { 'user' : user }, RequestContext(request))

def auth_settings(request, id):
    user_ = get_object_or_404(User, id=id)

    if not (request.user.is_superuser or request.user == user_):
        return HttpResponseUnauthorized(request)

    auth_keys = user_.auth_keys.all()

    if request.user.is_superuser or (not user_.has_usable_password()):
        FormClass = SetPasswordForm
    else:
        FormClass = ChangePasswordForm

    if request.POST:
        form = FormClass(request.POST, user=user_)
        if form.is_valid():
            is_new_pass = not user_.has_usable_password()
            user_.set_password(form.cleaned_data['password1'])
            user_.save()

            if is_new_pass:
                messages.success(request, message=_("New password set"))
                if not request.user.is_superuser:
                    form = ChangePasswordForm(user=user_)
            else:
                messages.success(request, message=_("Your password was changed"))

            return HttpResponseRedirect(reverse('user_authsettings', kwargs={'id': user_.id}))
    else:
        form = FormClass(user=user_)

    auth_keys_list = []

    for k in auth_keys:
        provider = AUTH_PROVIDERS.get(k.provider, None)

        if provider is not None:
            name =  "%s: %s" % (provider.context.human_name, provider.context.readable_key(k))
        else:
            from forum.authentication.base import ConsumerTemplateContext
            "unknown: %s" % ConsumerTemplateContext.readable_key(k)

        auth_keys_list.append({
        'name': name,
        'id': k.id
        })

    return render_to_response('auth/auth_settings.html', {
    'view_user': user_,
    "can_view_private": (user_ == request.user) or request.user.is_superuser,
    'form': form,
    'has_password': user_.has_usable_password(),
    'auth_keys': auth_keys_list,
    'allow_local_auth': AUTH_PROVIDERS.get('local', None),
    }, context_instance=RequestContext(request))

def remove_external_provider(request, id):
    association = get_object_or_404(AuthKeyUserAssociation, id=id)
    if not (request.user.is_superuser or request.user == association.user):
        return HttpResponseUnauthorized(request)

    messages.success(request, message=_("You removed the association with %s") % association.provider)
    association.delete()
    return HttpResponseRedirect(reverse('user_authsettings', kwargs={'id': association.user.id}))

def login_and_forward(request, user, forward=None, message=None):
    if user.is_suspended():
        return forward_suspended_user(request, user)

    user.backend = "django.contrib.auth.backends.ModelBackend"
    login(request, user)

    if message is None:
        message = _("Welcome back %s, you are now logged in") % user.first_name

    #request.user.message_set.create(message=message)
    messages.success(request, message)

    if not forward:
        forward = request.session.get(ON_SIGNIN_SESSION_ATTR, reverse('homepage'))

    pending_data = request.session.get(PENDING_SUBMISSION_SESSION_ATTR, None)

    if pending_data and (user.email_isvalid or pending_data['type'] not in settings.REQUIRE_EMAIL_VALIDATION_TO):
        submission_time = pending_data['time']
        if submission_time < datetime.datetime.now() - datetime.timedelta(minutes=int(settings.HOLD_PENDING_POSTS_MINUTES)):
            del request.session[PENDING_SUBMISSION_SESSION_ATTR]
        elif submission_time < datetime.datetime.now() - datetime.timedelta(minutes=int(settings.WARN_PENDING_POSTS_MINUTES)):
            user.message_set.create(message=(_("You have a %s pending submission.") % pending_data['data_name']) + " %s, %s, %s" % (
                html.hyperlink(reverse('manage_pending_data', kwargs={'action': _('save')}), _("save it")),
                html.hyperlink(reverse('manage_pending_data', kwargs={'action': _('review')}), _("review")),
                html.hyperlink(reverse('manage_pending_data', kwargs={'action': _('cancel')}), _("cancel"))
            ))
        else:
            return manage_pending_data(request, _('save'), forward)

    return HttpResponseRedirect(forward)

def forward_suspended_user(request, user, show_private_msg=True):
    message = _("Sorry, but this account is suspended")
    if show_private_msg:
        msg_type = 'privatemsg'
    else:
        msg_type = 'publicmsg'

    suspension = user.suspension
    if suspension:
        message += (":<br />" + suspension.extra.get(msg_type, ''))

    messages.error(request, message)
    return HttpResponseRedirect(reverse('homepage'))

@decorate.withfn(login_required)
def signout(request):
    logout(request)
    return HttpResponseRedirect(reverse('splash'))
