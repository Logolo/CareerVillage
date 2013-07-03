import logging

from django import template

# Obtain template library
register = template.Library()

# Obtain logger
logger = logging.getLogger('forum.templates')


@register.simple_tag(takes_context=True)
def log(context, message, method='info'):
    """ Register a log message using the specified method.
    """
    message = 'In path \'%s\': %s' % (context['request'].path, message)
    if method == 'debug':
        logger.debug(message)
    elif method == 'info':
        logger.info(message)
    elif method == 'error':
        logger.error(message)
    elif method == 'critical':
        logger.critical(message)


@register.simple_tag(takes_context=True)
def log_old_template(context):
    """ Register a log message when a v1 template is being used.
    """
    logger.info('Using a v1 template in path \'%s\'.' % context['request'].path)
