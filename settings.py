# encoding:utf-8
import os.path
import sys

SITE_ID = 1

ADMIN_MEDIA_PREFIX = '/admin_media/'
SECRET_KEY = '$oo^&_m&qwbib=(_4m_n*zn-d=g#s0he5fx9xonnym#8p6yigm'

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
    os.path.join(os.path.dirname(__file__),'forum','skins').replace('\\','/'),
)


FILE_UPLOAD_TEMP_DIR = os.path.join(os.path.dirname(__file__), 'tmp').replace('\\','/')
FILE_UPLOAD_HANDLERS = ("django.core.files.uploadhandler.MemoryFileUploadHandler",
 "django.core.files.uploadhandler.TemporaryFileUploadHandler",)
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

ALLOW_FILE_TYPES = ('.jpg', '.jpeg', '.gif', '.bmp', '.png', '.tiff')
ALLOW_MAX_FILE_SIZE = 1024 * 1024

FACEBOOK_APP_ID = '509955625712593'
FACEBOOK_APP_NAMESPACE = 'cv-dev-cc'
FACEBOOK_API_SECRET = '1cfa69cc598fc6526e6d975ec0761474'
FACEBOOK_EXTENDED_PERMISSIONS = ['email', 'publish_actions']

# User settings
from settings_local import *

try:
    if len(FORUM_SCRIPT_ALIAS) > 0:
        APP_URL = '%s/%s' % (APP_URL, FORUM_SCRIPT_ALIAS[:-1])
except NameError:
    pass

app_url_split = APP_URL.split("://")

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
MODULES_FOLDER = os.path.join(SITE_SRC_ROOT, MODULES_PACKAGE)

MODULE_LIST = filter(lambda m: getattr(m, 'CAN_USE', True), [
        __import__('forum_modules.%s' % f, globals(), locals(), ['forum_modules'])
        for f in os.listdir(MODULES_FOLDER)
        if os.path.isdir(os.path.join(MODULES_FOLDER, f)) and
           os.path.exists(os.path.join(MODULES_FOLDER, "%s/__init__.py" % f)) and
           not f in DISABLED_MODULES
])

[MIDDLEWARE_CLASSES.extend(
        ["%s.%s" % (m.__name__, mc) for mc in getattr(m, 'MIDDLEWARE_CLASSES', [])]
                          ) for m in MODULE_LIST]

[TEMPLATE_LOADERS.extend(
        ["%s.%s" % (m.__name__, tl) for tl in getattr(m, 'TEMPLATE_LOADERS', [])]
                          ) for m in MODULE_LIST]


INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.humanize',
    'django.contrib.sitemaps',
    'django.contrib.markup',
    'social_auth',
    'forum',
]

if DEBUG:
    try:
        import debug_toolbar
        MIDDLEWARE_CLASSES.append('debug_toolbar.middleware.DebugToolbarMiddleware')
        INSTALLED_APPS.append('debug_toolbar')
    except:
        pass

try:
    import south
    INSTALLED_APPS.append('south')
except:
    pass

if not DEBUG:
    try:
        import rosetta
        INSTALLED_APPS.append('rosetta')
    except:
        pass

#allows case insensitive login
AUTHENTICATION_BACKENDS = ('forum.authentication.backend.CaseInsensitiveModelBackend',
                           'social_auth.backends.facebook.FacebookBackend',
)
#AUTHENTICATION_BACKENDS = ['django.contrib.auth.backends.ModelBackend']
SOCIAL_AUTH_FIELDS_STORED_IN_SESSION = ['user_type']

SOCIAL_AUTH_COMPLETE_URL_NAME = 'socialauth_complete'
SOCIAL_AUTH_ASSOCIATE_URL_NAME = 'socialauth_associate_complete'

# SOCIAL_AUTH_USER_MODEL = 'forum.models.user.User'

SOCIAL_AUTH_PIPELINE = (

    'social_auth.backends.pipeline.social.social_auth_user',
    'social_auth.backends.pipeline.social.associate_user',
    'forum.authentication.pipeline.create_user',

    # 'social_auth.backends.pipeline.misc.save_status_to_session',

    'social_auth.backends.pipeline.user.create_user',
    'social_auth.backends.pipeline.social.associate_user',
    'social_auth.backends.pipeline.social.load_extra_data',
    'social_auth.backends.pipeline.user.update_user_details',
    'social_auth.backends.pipeline.misc.save_status_to_session',

)

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/home/'
LOGIN_ERROR_URL = '/login/'