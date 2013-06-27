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


# Obtain logger
logger = logging.getLogger('forum.actions.facebook')


class Graph(object):

    BASE_URL = "https://graph.facebook.com/"

    @classmethod
    def get_app_access_token(cls):
        response = urllib2.urlopen("%soauth/access_token?client_id=%s&client_secret=%s&grant_type=client_credentials" %
                                   (cls.BASE_URL, settings.FACEBOOK_APP_ID, settings.FACEBOOK_API_SECRET)).read()
        values = urlparse.parse_qs(response)
        return values['access_token'][0]

    @classmethod
    def extend_access_token(cls, token):
        response = urllib2.urlopen("%soauth/access_token?client_id=%s&client_secret=%s&fb_exchange_token=%s&grant_type=fb_exchange_token" % (
            cls.BASE_URL, settings.FACEBOOK_APP_ID, settings.FACEBOOK_API_SECRET, token)).read()
        values = urlparse.parse_qs(response)
        return values['access_token'][0], now() + datetime.timedelta(seconds=int(values['expires'][0]))

    @classmethod
    def get_user_id(cls, token):
        response = urllib2.urlopen("%sme?access_token=%s" % (cls.BASE_URL, token)).read()
        values = json.loads(response)
        return values['id']

    @classmethod
    def create_object(cls, object_type, object_data):
        """ Create an app-owned object and return its id.
        """
        app_object_type = '%s:%s' % (settings.FACEBOOK_APP_NAMESPACE, object_type)
        object_data.update({
            'type': app_object_type,
        })
        try:
            response = urllib2.urlopen("%sapp/objects/%s" % (cls.BASE_URL, app_object_type),
                                       urllib.urlencode({
                                           'access_token': cls.get_app_access_token(),
                                           'object': json.dumps(object_data)
                                       })).read()
            values = json.loads(response)
            return values['id']
        except urllib2.HTTPError, e:
            error = json.loads(e.read())
            logger.exception(error)
            raise GraphException(error['error'])


class GraphException(Exception):
    pass


class Story(Graph):

    def __init__(self, user, object):
        self._user = user
        self._object = object

    def get_url(self):
        pass

    def get_object_url(self):
        pass

    def get_data(self):
        pass

    def publish(self):
        url = self.get_url()
        data = self.get_data()
        data.update({
            'access_token': self._user.facebook_access_token
        })
        try:
            urllib2.urlopen(url, urllib.urlencode(data), timeout=30)
        except urllib2.HTTPError, e:
            error = json.loads(e.read())
            logger.exception(error)
            raise GraphException(error['error'])
        else:
            logger.info('User %s (fbid=%s) posted %s with object="%s".' % (
                self._user.username, self._user.facebook_uid, self.__class__.__name__, unicode(self._object)))



class Notification(Graph):

    def __init__(self, user):
        self._user = user

    def get_url(self):
        return "%s%s/notifications" % (self.BASE_URL, self._user.facebook_uid)

    def get_href(self):
        pass

    def get_template(self):
        pass

    def get_data(self):
        return {
            'href': self.get_href(),
            'template': self.get_template().encode('utf-8'),
            'access_token': self.get_app_access_token()
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
            logger.info('User %s (fbid=%s) has been notified "%s" (href="%s").' % (
                self._user.username, self._user.facebook_uid, data.get('template', ''), data.get('href', '')))


class LikeQuestionStory(Story):

    def get_url(self):
        return "%sme/og.likes" % (self.BASE_URL,)

    def get_object_url(self):
        return settings.APP_URL + reverse('question', kwargs={'id': self._object.id})

    def get_data(self):
        return {
            'object': 'http://samples.ogp.me/358120227643921' if settings.DEBUG else self.get_object_url(),
        }


class LikeAnswerStory(Story):

    def get_url(self):
        return "%sme/og.likes" % (self.BASE_URL,)

    def get_object_url(self):
        return settings.APP_URL + reverse('answer', kwargs={'id': self._object.id})

    def get_data(self):
        title = 'Answer to %s' % self._object.parent.title
        data = {
            'object': Graph.create_object('answer', {
                'title': title,
                'image': settings.APP_URL + media('/media/img/careervillage_256x256.png'),
                'url': 'http://samples.ogp.me/358124874310123' if settings.DEBUG else self.get_object_url(),
                'description': title,
            })
        }
        return data


class AskQuestionStory(Story):

    def __init__(self, question, message=None):
        super(AskQuestionStory, self).__init__(question.user, question)
        self._message = message

    def get_url(self):
        return "%sme/%s:ask" % (self.BASE_URL, settings.FACEBOOK_APP_NAMESPACE,)

    def get_object_url(self):
        return settings.APP_URL + reverse('question', kwargs={'id': self._object.id})

    def get_data(self):
        data = {
            'question': 'http://samples.ogp.me/358120227643921' if settings.DEBUG else self.get_object_url(),
        }
        if self._message:
            data['message'] = self._message
        return data


class AnswerQuestionStory(Story):

    def __init__(self, answer, message=None):
        super(AnswerQuestionStory, self).__init__(answer.author, answer.parent)
        self._message = message

    def get_url(self):
        return "%sme/%s:answer" % (self.BASE_URL, settings.FACEBOOK_APP_NAMESPACE,)

    def get_object_url(self):
        return settings.APP_URL + reverse('question', kwargs={'id': self._object.id})

    def get_data(self):
        data = {
            'question': 'http://samples.ogp.me/358120227643921' if settings.DEBUG else self.get_object_url(),
        }
        if self._message:
            data['message'] = self._message
        return data


class AwardBadgeStory(Story):

    def __init__(self, award):
        super(AwardBadgeStory, self).__init__(award.user, award.badge)

    def get_url(self):
        return "%sme/%s:award" % (self.BASE_URL, settings.FACEBOOK_APP_NAMESPACE,)

    def get_object_url(self):
        return settings.APP_URL + self._object.get_absolute_url()

    def get_data(self):
        data = {
            'badge': Graph.create_object('badge', {
                'title': self._object.name,
                'image': settings.APP_URL + media('/media/img/careervillage_256x256.png'),
                'url': 'http://samples.ogp.me/358124060976871' if settings.DEBUG else self.get_object_url(),
                'description': self._object.name,
            })
        }
        return data


class InterestTopicStory(Story):

    def __init__(self, user, topic):
        super(InterestTopicStory, self).__init__(user, topic)

    def get_url(self):
        return "%sme/%s:interest" % (self.BASE_URL, settings.FACEBOOK_APP_NAMESPACE,)

    def get_object_url(self):
        return settings.APP_URL + self._object.get_absolute_url()

    def get_data(self):
        data = {
            'topic': Graph.create_object('topic', {
                'title': self._object.name,
                'image': settings.APP_URL + media('/media/img/careervillage_256x256.png'),
                'url': 'http://samples.ogp.me/358123727643571' if settings.DEBUG else self.get_object_url(),
                'description': self._object.name,
            })
        }
        return data


class GetPointStory(Story):

    def __init__(self, user, point_count):
        super(GetPointStory, self).__init__(user, None)
        self._point_count = point_count

    def get_url(self):
        return "%sme/%s:get" % (self.BASE_URL, settings.FACEBOOK_APP_NAMESPACE)

    def get_object_url(self):
        return settings.APP_URL + self._user.get_profile_url() + '?point_count=%s' % self._point_count

    def get_data(self):
        data = {
            'point': Graph.create_object('point', {
                'title': '%s points' % self._point_count,
                'image': settings.APP_URL + media('/media/img/careervillage_256x256.png'),
                'url': 'http://samples.ogp.me/359065370882740' if settings.DEBUG else self.get_object_url(),
                'description': '%s points' % self._point_count,
                'data': {
                    'count': self._point_count,
                }
            })
        }
        return data


class ReachPointStory(Story):

    def __init__(self, user, point_count):
        super(ReachPointStory, self).__init__(user, None)
        self._point_count = point_count

    def get_url(self):
        return "%sme/%s:reach" % (self.BASE_URL, settings.FACEBOOK_APP_NAMESPACE)

    def get_object_url(self):
        return settings.APP_URL + self._user.get_profile_url() + '?point_count=%s' % self._point_count

    def get_data(self):
        data = {
            'point': Graph.create_object('point', {
                'title': '%s points' % self._point_count,
                'image': settings.APP_URL + media('/media/img/careervillage_256x256.png'),
                'url': 'http://samples.ogp.me/359065370882740' if settings.DEBUG else self.get_object_url(),
                'description': '%s points' % self._point_count,
                'data': {
                    'count': self._point_count,
                }
            })
        }
        return data


class AnswerQuestionNotification(Notification):

    def __init__(self, answer):
        super(AnswerQuestionNotification, self).__init__(answer.parent.author)
        self._question = answer.parent
        self._answerer = answer.author

    def get_href(self):
        return settings.APP_URL + reverse('question', kwargs={'id': self._question.id})

    def get_template(self):
        answerer_fb_uid = self._answerer.facebook_uid
        return _("%s just answered your question. Check it out and say thanks at %s.") % (
            self._answerer.display_name('safe') if not answerer_fb_uid else u'@[%s]' % answerer_fb_uid, self.get_href())


class TopicQuestionNotification(Notification):

    def __init__(self, user, question_count):
        super(TopicQuestionNotification, self).__init__(user)
        self._question_count = question_count

    def get_href(self):
        return settings.APP_URL + reverse('relevant')

    def get_template(self):
        return _("Over the last week, there have been %s questions about topics you are interested in.") \
                    % self._question_count


class AwardBadgeNotification(Notification):

    def __init__(self, award):
        super(AwardBadgeNotification, self).__init__(award.user)
        self._badge = award.badge

    def get_href(self):
        return settings.APP_URL + self._badge.get_absolute_url()

    def get_template(self):
        return _("You have been awarded %s on CareerVillage.") % self._badge.name