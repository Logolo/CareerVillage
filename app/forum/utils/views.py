from django.views.generic.base import RedirectView as BaseRedirectView
from django.core.urlresolvers import reverse


class RedirectView(BaseRedirectView):

    viewname = None

    def get_redirect_url(self, **kwargs):
        if self.viewname:
            url = reverse(self.viewname, kwargs=kwargs)
            args = self.request.META.get('QUERY_STRING', '')
            if args and self.query_string:
                url = "%s?%s" % (url, args)
            return url
        else:
            return super(RedirectView, self).get_redirect_url()
