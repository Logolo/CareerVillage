from django import template
from django.utils.safestring import mark_safe
import logging
import markdown
from forum.models import Node, Tag

register = template.Library()

@register.filter
def follows(user, question):
    if user.is_authenticated():
        return any([question.id == q.id for q in user.subscriptions.all()])
    else:
        return False


@template.defaultfilters.stringfilter
@register.filter
def collapse(input):
    return ' '.join(input.split())


@register.filter
def can_edit_post(user, post):
    return user.can_edit_post(post)


@register.filter
def decorated_int(number, cls="thousand"):
    try:
        number = int(number)    # allow strings or numbers passed in
        if number > 999:
            thousands = float(number) / 1000.0
            format = "%.1f" if number < 99500 else "%.0f"
            s = format % thousands

            return mark_safe("<span class=\"%s\">%sk</span>" % (cls, s))
        return number
    except:
        return number

@register.filter
def or_preview(setting, request):
    if request.user.is_superuser:
        previewing = request.session.get('previewing_settings', {})
        if setting and setting.name in previewing:
            return previewing[setting.name]
    return setting and setting.value

@register.filter
def getval(map, key):
    return map and map.get(key, None) or None


@register.filter
def contained_in(item, container):
    return item in container

@register.filter
def static_content(content, render_mode):
    if render_mode == 'markdown':
        return mark_safe(markdown.markdown(unicode(content), ["settingsparser"]))
    elif render_mode == "html":
        return mark_safe(unicode(content))
    else:
        return unicode(content)


@register.filter
def tag_slug(tag_name):
    return Tag.make_slug(tag_name)

