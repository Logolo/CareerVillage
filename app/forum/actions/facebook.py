# -*- coding: utf-8 -*-

import urllib2
import urllib
import json
import urlparse
import datetime
import logging

from django.core.urlresolvers import reverse
from django.conf import settings
from django.utils.translation import ugettext as _
from django.utils.timezone import now

from forum.templatetags.extra_tags import media
from forum.models import FacebookAccount, FacebookObject


# Obtain logger
logger = logging.getLogger('forum.actions.facebook')

# Get app-specific settings
FACEBOOK_APPS = settings.FACEBOOK_APPS


def get_app_id(app=None):
    if app:
        return FACEBOOK_APPS[app]['APP_ID']
    else:
        return settings.FACEBOOK_APP_ID


def get_app_namespace(app=None):
    if app:
        return FACEBOOK_APPS[app]['APP_NAMESPACE']
    else:
        return settings.FACEBOOK_APP_NAMESPACE


def get_api_secret(app=None):
    if app:
        return FACEBOOK_APPS[app]['API_SECRET']
    else:
        return settings.FACEBOOK_API_SECRET


def get_app_url(app=None):
    if app:
        return FACEBOOK_APPS[app]['APP_URL']
    else:
        return settings.FACEBOOK_APP_URL


def get_account(user, app=None):
    try:
        return user.facebook_accounts.get(app=(app or settings.FACEBOOK_APP))
    except FacebookAccount.DoesNotExist:
        pass


def get_full_url(url, app=None):
    return urlparse.urljoin(get_app_url(app), url)


def get_generic_image_url(app=None):
    return get_full_url(media('/media/img/careervillage_256x256.png'), app=app)


class Graph(object):

    BASE_URL = "https://graph.facebook.com/"

    @classmethod
    def get_app_access_token(cls, app=None):
        response = urllib2.urlopen("%soauth/access_token?client_id=%s&client_secret=%s&grant_type=client_credentials" %
                                   (cls.BASE_URL, get_app_id(app), get_api_secret(app))).read()
        values = urlparse.parse_qs(response)
        return values['access_token'][0]

    @classmethod
    def extend_access_token(cls, token, app=None):
        response = urllib2.urlopen(
            "%soauth/access_token?client_id=%s&client_secret=%s&fb_exchange_token=%s&grant_type=fb_exchange_token" % (
                cls.BASE_URL, get_app_id(app), get_api_secret(app), token)).read()
        values = urlparse.parse_qs(response)
        return values['access_token'][0], now() + datetime.timedelta(seconds=int(values['expires'][0]))

    @classmethod
    def get_user_id(cls, token):
        response = urllib2.urlopen("%sme?access_token=%s" % (cls.BASE_URL, token)).read()
        values = json.loads(response)
        return values['id']

    @classmethod
    def get_object(cls, object_type, object_data, app=None, model_id=None):
        """ Get or create an app-owned object and return its Facebook ID.
        """
        if model_id:
            app = app or settings.FACEBOOK_APP
            try:
                facebook_object = FacebookObject.objects.get(app=app, object_type=object_type, model_id=model_id)
                return facebook_object.object_id
            except FacebookObject.DoesNotExist:
                pass

        app_object_type = '%s:%s' % (get_app_namespace(app), object_type)
        object_data.update({
            'type': app_object_type,
        })
        try:
            response = urllib2.urlopen("%sapp/objects/%s" % (cls.BASE_URL, app_object_type),
                                       urllib.urlencode({
                                           'access_token': cls.get_app_access_token(app=app),
                                           'object': json.dumps(object_data)
                                       })).read()
            values = json.loads(response)
            object_id = values['id']

            # Store Facebook object
            if model_id:
                facebook_object = FacebookObject.objects.create(app=app, object_type=object_type, model_id=model_id,
                                                                object_id=object_id)

            return object_id
        except urllib2.HTTPError, e:
            error = json.loads(e.read())
            logger.exception(error)
            raise GraphException(error['error'])


class GraphException(Exception):
    pass


class Story(Graph):

    def __init__(self, user, obj, app=None):
        self._user = user
        self._object = obj
        self._app = app or settings.FACEBOOK_APP
        self._account = get_account(self._user, self._app)

    def get_app_namespace(self):
        return get_app_namespace(self._app)

    def get_url(self):
        pass

    def get_object_url(self):
        pass

    def get_object_full_url(self):
        return get_full_url(self.get_object_url(), app=self._app)

    def get_data(self):
        pass

    def publish(self):
        url = self.get_url()
        data = self.get_data()
        data.update({
            'access_token': self._account.access_token,
        })
        try:
            urllib2.urlopen(url, urllib.urlencode(data), timeout=30)
        except urllib2.HTTPError, e:
            error = json.loads(e.read())
            logger.exception(error)
            raise GraphException(error['error'])
        else:
            logger.info('[%s] User %s (fbid=%s) posted %s with object="%s".' % (
                self._app, self._user.username, self._account.uid,
                self.__class__.__name__, unicode(self._object)))


class Notification(Graph):

    def __init__(self, user, app=None):
        self._user = user
        self._app = app or settings.FACEBOOK_APP
        self._account = get_account(self._user, self._app)

    def get_url(self):
        return "%s%s/notifications" % (self.BASE_URL, self._account.uid)

    def get_href(self):
        pass

    def get_full_href(self):
        return get_full_url(self.get_href(), app=self._app)

    def get_template(self):
        pass

    def get_data(self):
        return {
            'href': self.get_full_href(),
            'template': self.get_template().encode('utf-8'),
            'access_token': self.get_app_access_token(app=self._app)
        }

    def notify(self):
        data = self.get_data()
        try:
            urllib2.urlopen(self.get_url(), urllib.urlencode(data), timeout=30)
        except urllib2.HTTPError, e:
            error = json.loads(e.read())
            logger.exception(error)
            raise GraphException(error['error'])
        else:
            logger.info('[%s] User %s (fbid=%s) has been notified "%s" (href="%s").' % (
                self._app, self._user.username,
                self._account.uid, data.get('template', ''), data.get('href', '')))


class LikeQuestionStory(Story):

    def get_url(self):
        return "%sme/og.likes" % (self.BASE_URL,)

    def get_object_url(self):
        return reverse('question', kwargs={'id': self._object.id})

    def get_data(self):
        title = self._object.title
        return {
            'object': Graph.get_object('question', {
                'title': title,
                'image': get_generic_image_url(app=self._app),
                'url': 'http://samples.ogp.me/358120227643921' if settings.DEBUG else self.get_object_full_url(),
                #'description': title,
            }, model_id=self._object.id)
        }


class LikeAnswerStory(Story):

    def get_url(self):
        return "%sme/og.likes" % (self.BASE_URL,)

    def get_object_url(self):
        return reverse('answer', kwargs={'id': self._object.id})

    def get_data(self):
        title = 'Answer to %s' % self._object.parent.title
        data = {
            'object': Graph.get_object('answer', {
                'title': title,
                'image': get_generic_image_url(app=self._app),
                'url': 'http://samples.ogp.me/358124874310123' if settings.DEBUG else self.get_object_full_url(),
                #'description': title,
            }, model_id=self._object.id)
        }
        return data


class AskQuestionStory(Story):

    def __init__(self, question, message=None, app=None):
        super(AskQuestionStory, self).__init__(question.user, question, app=app)
        self._message = message

    def get_url(self):
        return "%sme/%s:ask" % (self.BASE_URL, self.get_app_namespace(),)

    def get_object_url(self):
        return reverse('question', kwargs={'id': self._object.id})

    def get_data(self):
        data = {
            'question': Graph.get_object('question', {
                'title': self._object.title,
                'image': get_generic_image_url(app=self._app),
                'url': self.get_object_full_url(),
            }, model_id=self._object.id)
        }
        if self._message:
            data['message'] = self._message
        return data


class AnswerQuestionStory(Story):

    def __init__(self, answer, message=None, app=None):
        super(AnswerQuestionStory, self).__init__(answer.author, answer.parent, app=app)
        self._message = message

    def get_url(self):
        return "%sme/%s:answer" % (self.BASE_URL, self.get_app_namespace(),)

    def get_object_url(self):
        return reverse('question', kwargs={'id': self._object.id})

    def get_data(self):
        data = {
            'question': Graph.get_object('question', {
                'title': self._object.title,
                'image': get_generic_image_url(app=self._app),
                'url': 'http://samples.ogp.me/358120227643921' if settings.DEBUG else self.get_object_full_url(),
            }, model_id=self._object.id)
        }
        if self._message:
            data['message'] = self._message
        return data


class AwardBadgeStory(Story):

    def __init__(self, award, app=None):
        super(AwardBadgeStory, self).__init__(award.user, award.badge, app=app)

    def get_url(self):
        return "%sme/%s:award" % (self.BASE_URL, self.get_app_namespace(),)

    def get_object_url(self):
        return self._object.get_absolute_url()

    def get_data(self):
        data = {
            'badge': Graph.get_object('badge', {
                'title': self._object.name,
                'image': get_generic_image_url(app=self._app),
                'url': 'http://samples.ogp.me/358124060976871' if settings.DEBUG else self.get_object_full_url(),
                #'description': self._object.name,
            }, model_id=self._object.id)
        }
        return data


class InterestTopicStory(Story):

    def get_url(self):
        return "%sme/%s:interest" % (self.BASE_URL, self.get_app_namespace(),)

    def get_object_url(self):
        return self._object.get_absolute_url()

    def get_data(self):
        data = {
            'topic': Graph.get_object('topic', {
                'title': self._object.name,
                'image': get_generic_image_url(app=self._app),
                'url': 'http://samples.ogp.me/358123727643571' if settings.DEBUG else self.get_object_full_url(),
                #'description': self._object.name,
            }, model_id=self._object.id)
        }
        return data


class GetPointStory(Story):

    def __init__(self, user, point_count, app=None):
        super(GetPointStory, self).__init__(user, None, app=app)
        self._point_count = point_count

    def get_url(self):
        return "%sme/%s:get" % (self.BASE_URL, self.get_app_namespace())

    def get_object_url(self):
        return self._user.get_profile_url() + '?point_count=%s' % self._point_count

    def get_data(self):
        data = {
            'point': Graph.get_object('point', {
                'title': '%s points' % self._point_count,
                'image': get_generic_image_url(app=self._app),
                'url': 'http://samples.ogp.me/359065370882740' if settings.DEBUG else self.get_object_full_url(),
                #'description': '%s points' % self._point_count,
                'data': {
                    'count': self._point_count,
                }
            })
        }
        return data


class ReachPointStory(Story):

    def __init__(self, user, point_count, app=None):
        super(ReachPointStory, self).__init__(user, None, app=app)
        self._point_count = point_count

    def get_url(self):
        return "%sme/%s:reach" % (self.BASE_URL, self.get_app_namespace())

    def get_object_url(self):
        return self._user.get_profile_url() + '?point_count=%s' % self._point_count

    def get_data(self):
        data = {
            'point': Graph.get_object('point', {
                'title': '%s points' % self._point_count,
                'image': get_generic_image_url(app=self._app),
                'url': 'http://samples.ogp.me/359065370882740' if settings.DEBUG else self.get_object_full_url(),
                #'description': '%s points' % self._point_count,
                'data': {
                    'count': self._point_count,
                }
            })
        }
        return data


class AnswerQuestionNotification(Notification):

    def __init__(self, answer, app=None):
        super(AnswerQuestionNotification, self).__init__(answer.parent.author, app=app)
        self._question = answer.parent
        self._answerer = answer.author

    def get_href(self):
        return settings.APP_URL + reverse('question', kwargs={'id': self._question.id})

    def get_template(self):
        answerer_fb_uid = self._answerer.facebook_uid
        return _("%s just answered your question. Check it out and say thanks at %s.") % (
            self._answerer.display_name('safe') if not answerer_fb_uid else u'@[%s]' % answerer_fb_uid,
            self.get_full_href())


class TopicQuestionNotification(Notification):

    def __init__(self, user, question_count, app=None):
        super(TopicQuestionNotification, self).__init__(user, app=app)
        self._question_count = question_count

    def get_href(self):
        return settings.APP_URL + reverse('relevant')

    def get_template(self):
        return _("Over the last week, there have been %s questions about topics you are interested in.") \
                    % self._question_count


class AwardBadgeNotification(Notification):

    def __init__(self, award, app=None):
        super(AwardBadgeNotification, self).__init__(award.user, app=app)
        self._badge = award.badge

    def get_href(self):
        return settings.APP_URL + self._badge.get_absolute_url()

    def get_template(self):
        return _("You have been awarded %s on CareerVillage.") % self._badge.name