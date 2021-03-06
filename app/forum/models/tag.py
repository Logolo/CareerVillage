import re
import datetime
import unicodedata
from base import *

from django.utils.translation import ugettext as _
from django.template.defaultfilters import slugify

from forum import modules


class ActiveTagManager(models.Manager):

    def get_query_set(self):
        return super(ActiveTagManager, self).get_query_set().exclude(used_count__lt=1)


class Tag(BaseModel):

    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)

    created_by = models.ForeignKey(User, related_name='created_tags')
    created_at = models.DateTimeField(default=datetime.datetime.now, blank=True, null=True)
    marked_by = models.ManyToManyField(User, related_name="marked_tags", through="MarkedTag")

    # Denormalised data
    used_count = models.PositiveIntegerField(default=0)

    active = ActiveTagManager()

    def save(self, *args, **kwargs):
        self.name = self.make_name(self.name)
        if not self.slug:
            self.slug = self.make_slug(self.name)
        super(Tag, self).save(*args, **kwargs)

    @classmethod
    def make_name(cls, tag_name):
        return re.sub('[-\s]+', '-', tag_name.lower())

    @classmethod
    def make_slug(cls, tag_name):
        nkfd_form = unicodedata.normalize('NFKD', unicode(tag_name))
        u_str = u"".join([c for c in nkfd_form if not unicodedata.combining(c)])
        return slugify(u_str)

    class Meta:
        ordering = ('-used_count', 'name')
        app_label = 'forum'

    def __unicode__(self):
        return u'%s' % self.name

    def add_to_usage_count(self, value):
        if self.used_count + value < 0:
            self.used_count = 0
        else:
            self.used_count = models.F('used_count') + value

    @models.permalink
    def get_absolute_url(self):
        return ('tag_questions', (), {'tag': self.name})


class MarkedTag(models.Model):

    TAG_MARK_REASONS = (('good', _('interesting')), ('bad', _('ignored')))
    tag = models.ForeignKey(Tag, related_name='user_selections')
    user = models.ForeignKey(User, related_name='tag_selections')
    reason = models.CharField(max_length=16, choices=TAG_MARK_REASONS)

    class Meta:
        app_label = 'forum'


def publish_interest_topic(sender, instance, created, **kwargs):
    from forum.tasks import facebook_interest_topic_story
    if created and instance.reason == 'good' and instance.user.can_facebook_interest_topic_story:
        facebook_interest_topic_story.apply_async(countdown=10, args=(instance.user.id, instance.tag.id))

post_save.connect(publish_interest_topic, sender=MarkedTag)
