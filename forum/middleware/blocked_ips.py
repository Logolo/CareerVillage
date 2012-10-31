from django.conf import settings
from django import http

class BlockedIpMiddleware(object):

    def process_request(self, request):
    	print "Checking for BLOCKED_IPS"
        if request.META['REMOTE_ADDR'] in settings.BLOCKED_IPS:
        	print "THIS IP IS BLOCKED"
            return http.HttpResponseForbidden('<h1>Forbidden</h1>')
        print "This IP is valid."
        return None

"""
simple middlware to block IP addresses via settings variable BLOCKED_IPS
"""
