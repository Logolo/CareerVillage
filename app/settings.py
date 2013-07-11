# encoding:utf-8
import os.path
import djcelery


APP_ROOT = os.path.dirname(__file__)


def rel(*x):
    return os.path.join(APP_ROOT, *x)

DEBUG = False
TEMPLATE_DEBUG = False

ADMINS = (
    ('Team', 'team@gathereducation.com'),
)
MANAGERS = ADMINS

SITE_ID = 1

TIME_ZONE = 'America/New_York'
LANGUAGE_CODE = 'en'
USE_I18N = True
USE_L10N = False

OSQA_DEFAULT_SKIN = 'default'

DATABASES = None

SECRET_KEY = None

ADMIN_MEDIA_PREFIX = '/admin_media/'

AWS_ACCESS_KEY_ID = None
AWS_SECRET_ACCESS_KEY = None

INSTALLED_APPS = [
    'longerusername',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.humanize',
    'django.contrib.sitemaps',
    'django.contrib.markup',

    'social_auth',
    'djcelery',
    'forum',
    'raven.contrib.django.raven_compat',
    'south',
]


TEMPLATE_LOADERS = [
    #'django.template.loaders.filesystem.load_template_source',
    #'django.template.loaders.app_directories.load_template_source',
    'django.template.loaders.app_directories.Loader',
    'forum.modules.template_loader.module_templates_loader',
    'forum.skins.load_template_source',
]

MIDDLEWARE_CLASSES = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.common.CommonMiddleware',
    'forum.middleware.extended_user.ExtendedUser',
    'forum.middleware.anon_user.ConnectToSessionMessagesMiddleware',
    'forum.middleware.request_utils.RequestUtils',
    'forum.middleware.cancel.CancelActionMiddleware',
    'forum.middleware.admin_messages.AdminMessagesMiddleware',
    'forum.middleware.blocked_ips.BlockedIpMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
]

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.request',
    'forum.context.application_settings',
    'forum.user_messages.context_processors.user_messages',
    #'django.core.context_processors.auth',
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',

    'social_auth.context_processors.social_auth_by_name_backends',
    'social_auth.context_processors.social_auth_backends',
    'social_auth.context_processors.social_auth_by_type_backends',
    'social_auth.context_processors.social_auth_login_redirect',
)

ROOT_URLCONF = 'urls'
APPEND_SLASH = True

TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(__file__), 'forum', 'skins').replace('\\','/'),
)

DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
FILE_UPLOAD_TEMP_DIR = os.path.join(os.path.dirname(__file__), 'tmp').replace('\\','/')
FILE_UPLOAD_HANDLERS = ('django.core.files.uploadhandler.MemoryFileUploadHandler',
                        'django.core.files.uploadhandler.TemporaryFileUploadHandler',)
ALLOW_FILE_TYPES = ('.jpg', '.jpeg', '.gif', '.bmp', '.png', '.tiff')
ALLOW_MAX_FILE_SIZE = 1024 * 1024

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/home/'
LOGIN_ERROR_URL = '/login/'

AUTHENTICATION_BACKENDS = (
   'social_auth.backends.facebook.FacebookBackend',
   'social_auth.backends.contrib.linkedin.LinkedinOAuth2Backend',
   'forum.authentication.backend.CaseInsensitiveModelBackend',
)

SOCIAL_AUTH_SLUGIFY_USERNAME = False
SOCIAL_AUTH_USERNAME_IS_FULL_EMAIL = True
SOCIAL_AUTH_FIELDS_STORED_IN_SESSION = ['user_type']
SOCIAL_AUTH_COMPLETE_URL_NAME = 'socialauth_complete'
SOCIAL_AUTH_ASSOCIATE_URL_NAME = 'socialauth_associate_complete'
SOCIAL_AUTH_PIPELINE = (
    'social_auth.backends.pipeline.social.social_auth_user',
    'forum.authentication.pipeline.create_user',
    'social_auth.backends.pipeline.social.associate_user',
    'social_auth.backends.pipeline.social.load_extra_data',
    'forum.authentication.pipeline.login',
)

FACEBOOK_APP_ID = None
FACEBOOK_APP_NAMESPACE = None
FACEBOOK_API_SECRET = None
FACEBOOK_EXTENDED_PERMISSIONS = ['email', 'publish_actions']
FACEBOOK_EXTENDED_PERMISSIONS_STRING = ','.join(FACEBOOK_EXTENDED_PERMISSIONS)
# Minimum reputation increase when posting to Facebook
FACEBOOK_POST_REPUTATION_DELTA = 10
# Reputation multiple (user reached: 250, 500, 750, 1000, ... points)
FACEBOOK_POST_REPUTATION_MULTIPLE = 250
# Facebook permissions allowed by default
FACEBOOK_DEFAULT_SETTINGS = ['facebook_interest_topic_story',
                             'facebook_get_point_story',
                             'facebook_reach_point_story',
                             'facebook_answer_question_notification',
                             'facebook_topic_question_notification',
                             'facebook_award_badge_notification']
# Facebook permissions that can be updated using an AJAX call
FACEBOOK_ALLOW_SETTINGS_UPDATE = ['facebook_like_question_story',
                                  'facebook_like_answer_story',
                                  'facebook_ask_question_story',
                                  'facebook_answer_question_story']

LINKEDIN_CONSUMER_KEY = None
LINKEDIN_CONSUMER_SECRET = None
LINKEDIN_SCOPE = ['r_basicprofile', 'r_emailaddress', 'r_fullprofile']
LINKEDIN_EXTRA_FIELD_SELECTORS = ['id', 'skills', 'interests', 'first-name',
                                  'last-name', 'email-address', 'headline', 'industry',
                                  'picture-url', 'location']

# Default email notifications level
# ('I'=immediate, 'D'=daily, 'W'=weekly, 'N'=no notifications)
DEFAULT_NOTIFICATIONS = 'I'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

SESSION_ENGINE = 'django.contrib.sessions.backends.db'

#SENTRY-RAVEN
SENTRY_DSN = None
RAVEN_CONFIG = {
    'timeout': 30
}

#CELERY-RABBIT
BROKER_URL = 'amqp://guest:guest@localhost:5672/'
djcelery.setup_loader()

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

DISABLED_MODULES = ['books', 'recaptcha', 'project_badges']
BLOCK_TEST = None


try:
    from settings_local import *
except ImportError:
    pass


try:
    from settings_user import *
except ImportError:
    pass

app_url_split = APP_URL.split('://')

APP_PROTOCOL = app_url_split[0]
APP_DOMAIN = app_url_split[1].split('/')[0]
APP_BASE_URL = '%s://%s' % (APP_PROTOCOL, APP_DOMAIN)

FORCE_SCRIPT_NAME = ''

for path in app_url_split[1].split('/')[1:]:
    FORCE_SCRIPT_NAME = FORCE_SCRIPT_NAME + '/' + path

if FORCE_SCRIPT_NAME.endswith('/'):
    FORCE_SCRIPT_NAME = FORCE_SCRIPT_NAME[:-1]

#Module system initialization
MODULES_PACKAGE = 'forum_modules'
MODULES_FOLDER = os.path.join(APP_ROOT, MODULES_PACKAGE)

MODULE_LIST = filter(lambda m: getattr(m, 'CAN_USE', True), [
    __import__('forum_modules.%s' % f, globals(), locals(), ['forum_modules'])
    for f in os.listdir(MODULES_FOLDER)
    if os.path.isdir(os.path.join(MODULES_FOLDER, f)) and
       os.path.exists(os.path.join(MODULES_FOLDER, '%s/__init__.py' % f)) and
       not f in DISABLED_MODULES
])

[MIDDLEWARE_CLASSES.extend(
        ['%s.%s' % (m.__name__, mc) for mc in getattr(m, 'MIDDLEWARE_CLASSES', [])]) for m in MODULE_LIST]

[TEMPLATE_LOADERS.extend(
        ['%s.%s' % (m.__name__, tl) for tl in getattr(m, 'TEMPLATE_LOADERS', [])]) for m in MODULE_LIST]


LOGGING_LEVEL = 'DEBUG' if DEBUG else 'INFO'
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'sentry': {
            'level': LOGGING_LEVEL,
            'class': 'raven.handlers.logging.SentryHandler',
            'dsn': SENTRY_DSN
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['console', 'sentry'],
            'level': LOGGING_LEVEL,
            'propagate': False
        },
        'sentry.errors': {
            'handlers': ['console'],
            'level': LOGGING_LEVEL,
            'propagate': False
        },
        'forum': {
            'handlers': ['console', 'sentry'],
            'level': LOGGING_LEVEL,
            'propagate': False
        },
        'forum.actions.facebook': {
            'handlers': ['console', 'sentry'],
            'level': LOGGING_LEVEL,
            'propagate': False
        },
        'forum.management.commands.database_dump': {
            'handlers': ['console', 'sentry'],
            'level': LOGGING_LEVEL,
            'propagate': False
        },
        'forum.templates': {
            'handlers': ['console', 'sentry'],
            'level': LOGGING_LEVEL,
            'propagate': False
        }
    }
}

# Debug toolbar
if DEBUG:
    try:
        import debug_toolbar

        STATIC_URL = '/debug_toolbar/'
        INTERNAL_IPS = ('127.0.0.1',)

        def callback(request):
            return DEBUG and request.META['REMOTE_ADDR'] in INTERNAL_IPS

        DEBUG_TOOLBAR_CONFIG = {
            'INTERCEPT_REDIRECTS': False,
            'SHOW_TOOLBAR_CALLBACK': callback,
        }
        MIDDLEWARE_CLASSES += ['debug_toolbar.middleware.DebugToolbarMiddleware']
        INSTALLED_APPS += ['debug_toolbar']
        DEBUG_TOOLBAR_PANELS = (
            'debug_toolbar.panels.version.VersionDebugPanel',
            'debug_toolbar.panels.timer.TimerDebugPanel',
            'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
            'debug_toolbar.panels.headers.HeaderDebugPanel',
            #'debug_toolbar.panels.profiling.ProfilingDebugPanel',
            'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
            'debug_toolbar.panels.sql.SQLDebugPanel',
            'debug_toolbar.panels.template.TemplateDebugPanel',
            'debug_toolbar.panels.cache.CacheDebugPanel',
            'debug_toolbar.panels.signals.SignalDebugPanel',
            'debug_toolbar.panels.logger.LoggingPanel',
        )

    except ImportError:
        pass


if not DEBUG:
    try:
        import rosetta
        INSTALLED_APPS.append('rosetta')
    except ImportError:
        pass