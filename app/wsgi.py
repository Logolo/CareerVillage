import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

try:
    import newrelic.agent
    config_file = os.environ.get('NEW_RELIC_CONFIG_FILE', None)
    if config_file:
        newrelic.agent.initialize(config_file)
        application = newrelic.agent.wsgi_application()(application)
except ImportError:
    pass



