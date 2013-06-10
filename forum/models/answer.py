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


def publish_answer_question(sender, instance, created, **kwargs):
    from forum.tasks import answer_question_story
    if created and instance.user.can_publish_new_answer:
        answer_question_story.apply_async(countdown=10, args=(instance.id,))

post_save.connect(publish_answer_question, sender=Answer)


def notify_answer_question(sender, instance, created, **kwargs):
    from forum.tasks import answer_question_notification
    user = instance.parent.user
    if created and user.subscription_settings.notify_answers and user.is_student():
        answer_question_notification.apply_async(countdown=10, args=(instance.id,))

post_save.connect(notify_answer_question, sender=Answer)