from base import *
from django.utils.translation import ugettext as _

class Answer(Node):
    friendly_name = _("answer")

    class Meta(Node.Meta):
        proxy = True

    @property
    def accepted(self):
        return self.nis.accepted

    @property
    def headline(self):
        return self.question.headline

    def get_absolute_url(self):
        return '%s/%s' % (self.question.get_absolute_url(), self.id)


class AnswerRevision(NodeRevision):
    class Meta:
        proxy = True


def notify_new_answer(sender, instance, created, **kwargs):
    from forum.tasks import answer_notification
    if created and instance.parent.user.subscription_settings.notify_answers:
        answer_notification.apply_async(countdown=10, args=(instance.id,))

post_save.connect(notify_new_answer, sender=Answer)
