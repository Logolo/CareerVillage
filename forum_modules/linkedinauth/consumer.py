import urllib
import urllib2
import uuid

from django.utils.translation import ugettext as _
from django.utils import simplejson as json
from forum.authentication.base import AuthenticationConsumer, InvalidAuthentication

import settings

class OAuthAbstractAuthConsumer(AuthenticationConsumer):

    def __init__(self, consumer_key, consumer_secret, access_token_url, authorization_url):
        self.consumer_secret = consumer_secret
        self.consumer_key = consumer_key

        self.access_token_url = access_token_url
        self.authorization_url = authorization_url

    def prepare_authentication_request(self, request, redirect_to):
        request.session['linkedin_redirect_to'] = request.build_absolute_uri(redirect_to)
        request.session['linkedin_state'] = str(uuid.uuid4())
        params = {
            'response_type': 'code',
            'client_id': self.consumer_key,
            'scope': 'r_fullprofile',
            'state': request.session['linkedin_state'],
            'redirect_uri': request.session['linkedin_redirect_to']
        }
        data = urllib.urlencode(params)
        full_url='%s?%s' % (self.authorization_url, data)
        return full_url

    def process_authentication_request(self, request):
        try:
            if request.GET['state'] != request.session.pop('linkedin_state'):
                return
            params = {
                'grant_type': 'authorization_code',
                'code': request.GET['code'],
                'redirect_uri': request.session.pop('linkedin_redirect_to'),
                'client_id': self.consumer_key,
                'client_secret': self.consumer_secret
            }
            data = urllib.urlencode(params)
            full_url='%s?%s'%(self.access_token_url, data)
            url_request = urllib2.Request(full_url)
            response = urllib2.urlopen(url_request)        
            response = json.loads(response.read())

            request.session['oauth2_access_token'] = response['access_token']
            response = self.fetch_data(response['access_token'], 'https://api.linkedin.com/v1/people/~:(id)')            
            return response['id']
        except:
            return

    def fetch_data(self, token, http_url, parameters=None):
        full_url='%s?format=json&oauth2_access_token=%s'%(http_url, token)
        response = urllib2.urlopen(full_url)

        return json.loads(response.read())

