# -*- coding: utf-8 -*-
import urllib2
import urllib
import json

from django.core.urlresolvers import reverse
from django.conf import settings


class FacebookStory(object):

    BASE_URL = "https://graph.facebook.com/"

    def __init__(self, user, obj):
        self._user = user
        self._obj = obj

    def get_url(self):
        pass

    def get_obj_url(self):
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

    def get_obj_url(self):
        return settings.APP_URL + reverse('question', kwargs={'id': self._obj.id})

    def get_data(self):
        return {
            'object': self.get_obj_url(),
        }


class NewQuestion(FacebookStory):

    def get_url(self):
        return "%sme/%s:ask" % (self.BASE_URL, settings.FACEBOOK_APP_NAMESPACE,)

    def get_obj_url(self):
        return settings.APP_URL + reverse('question', kwargs={'id': self._obj.id})

    def get_data(self):
        return {
            #TODO: use for staging
            'question': self.get_obj_url(),
            #'question': 'http://samples.ogp.me/523169144391241',
            'title': "Test Question",
            'og:url': self.get_obj_url(),
        }


class OpenGraphError(Exception):
    pass
