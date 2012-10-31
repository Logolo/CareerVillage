from django.conf import settings
from django import http
import logging

class BlockedIpMiddleware(object):

    def process_request(self, request):
        if request.META['HTTP_X_FORWARDED_FOR'] in settings.BLOCKED_IPS:
        	logging.error("REQUEST FROM IP %s BLOCKED" % (request.META['HTTP_X_FORWARDED_FOR']))
            return http.HttpResponseForbidden('<h1>Forbidden</h1>')
        return None

"""
simple middlware to block IP addresses via settings variable BLOCKED_IPS
"""
