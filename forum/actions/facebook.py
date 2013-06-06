# -*- coding: utf-8 -*-
import urllib2
import urllib
import json

from django.core.urlresolvers import reverse
from django.conf import settings
from django.utils.translation import ugettext as _


class Facebook(object):

    BASE_URL = "https://graph.facebook.com/"

    def get_app_access_token(self):
        response = urllib2.urlopen("%soauth/access_token?client_id=%s&client_secret=%s&grant_type=client_credentials" % (
                self.BASE_URL, settings.FACEBOOK_APP_ID, settings.FACEBOOK_API_SECRET)).read()
        name, value = response.split('=')
        return value


class FacebookStory(Facebook):

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
            raise OpenGraphError(error['error'])


class FacebookNotification(Facebook):

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
            raise OpenGraphError(error['error'])


class LikeQuestion(FacebookStory):

    def get_url(self):
        return "%sme/og.likes" % (self.BASE_URL,)

    def get_object_url(self):
        return settings.APP_URL + reverse('question', kwargs={'id': self._object.id})

    def get_data(self):
        return {
            'object': self.get_object_url(),
        }


class NewQuestion(FacebookStory):

    def __init__(self, question, message=None):
        super(NewQuestion, self).__init__(question.user, question)
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


class AnswerNotification(FacebookNotification):

    def __init__(self, answer):
        super(AnswerNotification, self).__init__(answer.parent.author)
        self._question = answer.parent
        self._answerer = answer.author

    def get_href(self):
        return settings.APP_URL + reverse('question', kwargs={'id': self._question.id})

    def get_template(self):
        return _("%s just answered your question. Check it out and say thanks at %s.") % (
            self._answerer.display_name('safe'), self.get_href())


class OpenGraphError(Exception):
    pass