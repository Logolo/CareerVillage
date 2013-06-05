# -*- coding: utf-8 -*-
import urllib2
import urllib
import json

from django.core.urlresolvers import reverse
from django.conf import settings


class FacebookStory(object):

    BASE_URL = "https://graph.facebook.com/"

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

    def __init__(self, user, object, message=None):
        super(NewQuestion, self).__init__(user, object)
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


class OpenGraphError(Exception):
    pass
