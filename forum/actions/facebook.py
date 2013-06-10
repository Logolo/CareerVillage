# -*- coding: utf-8 -*-
import urllib2
import urllib
import json

from django.core.urlresolvers import reverse
from django.conf import settings
from django.utils.translation import ugettext as _


class Graph(object):

    BASE_URL = "https://graph.facebook.com/"

    def get_app_access_token(self):
        response = urllib2.urlopen("%soauth/access_token?client_id=%s&client_secret=%s&grant_type=client_credentials" % (
                self.BASE_URL, settings.FACEBOOK_APP_ID, settings.FACEBOOK_API_SECRET)).read()
        name, value = response.split('=')
        return value


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
            urllib2.urlopen(url, urllib.urlencode(data))
        except urllib2.HTTPError, e:
            error = json.loads(e.read())
            raise GraphException(error['error'])


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
            'template': self.get_template(),
            'access_token': self.get_app_access_token()
        }

    def notify(self):
        try:
            urllib2.urlopen(self.get_url(), urllib.urlencode(self.get_data()))
        except urllib2.HTTPError, e:
            error = json.loads(e.read())
            raise GraphException(error['error'])


class LikeQuestionStory(Story):

    def get_url(self):
        return "%sme/og.likes" % (self.BASE_URL,)

    def get_object_url(self):
        return settings.APP_URL + reverse('question', kwargs={'id': self._object.id})

    def get_data(self):
        return {
            'object': self.get_object_url(),
        }


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
            'question': 'http://samples.ogp.me/523169144391241' if settings.DEBUG else self.get_object_url(),
        }
        if self._message:
            data['message'] = self._message
        return data


class NewAnswerStory(Story):

    def __init__(self, answer, message=None):
        super(NewAnswerStory, self).__init__(answer.author, answer.parent)
        self._message = message

    def get_url(self):
        return "%sme/%s:answer" % (self.BASE_URL, settings.FACEBOOK_APP_NAMESPACE,)

    def get_object_url(self):
        return settings.APP_URL + reverse('question', kwargs={'id': self._object.id})

    def get_data(self):
        data = {
            'question': 'http://samples.ogp.me/523169144391241' if settings.DEBUG else self.get_object_url(),
        }
        if self._message:
            data['message'] = self._message
        return data


class NewAwardStory(Story):

    def __init__(self, award):
        super(NewAwardStory, self).__init__(award.user, award.badge)

    def get_url(self):
        return "%sme/%s:award" % (self.BASE_URL, settings.FACEBOOK_APP_NAMESPACE,)

    def get_object_url(self):
        return settings.APP_URL + self._object.get_absolute_url()

    def get_data(self):
        data = {
            'badge': 'http://samples.ogp.me/540345576006931' if settings.DEBUG else self.get_object_url(),
        }
        return data


class FollowTopicStory(Story):

    def __init__(self, user, topic):
        super(FollowTopicStory, self).__init__(user, topic)

    def get_url(self):
        return "%sme/%s:interest" % (self.BASE_URL, settings.FACEBOOK_APP_NAMESPACE,)

    def get_object_url(self):
        return settings.APP_URL + self._object.get_absolute_url()

    def get_data(self):
        data = {
            'topic': 'http://samples.ogp.me/540313696010119' if settings.DEBUG else self.get_object_url(),
        }
        return data


class AnswerNotification(Notification):

    def __init__(self, answer):
        super(AnswerNotification, self).__init__(answer.parent.author)
        self._question = answer.parent
        self._answerer = answer.author

    def get_href(self):
        return settings.APP_URL + reverse('question', kwargs={'id': self._question.id})

    def get_template(self):
        return _("%s just answered your question. Check it out and say thanks at %s.") % (
            self._answerer.display_name('safe'), self.get_href())


class WeeklyNotification(Notification):

    def __init__(self, user, question_count):
        super(WeeklyNotification, self).__init__(user)
        self._question_count = question_count

    def get_href(self):
        return settings.APP_URL + reverse('relevant')

    def get_template(self):
        return _("Over the last week, there have been %s questions about topics you are interested in.") \
                    % self._question_count
