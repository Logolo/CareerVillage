from django.conf import settings
from django import http
import logging

class BlockedIpMiddleware(object):

    def process_request(self, request):
        logging.error("Checking %s for BLOCKED_IPS" % (request.META['REMOTE_ADDR']))
        if request.META['REMOTE_ADDR'] in settings.BLOCKED_IPS:
            logging.error("THIS IP IS BLOCKED")
            return http.HttpResponseForbidden('<h1>Forbidden</h1>')
        logging.error("This IP is valid.")
        return None

"""
simple middlware to block IP addresses via settings variable BLOCKED_IPS
"""
