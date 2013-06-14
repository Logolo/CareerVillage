from datetime import datetime, timedelta

from django.core.management.base import NoArgsCommand
from django.db.models import Q

from forum.models import User, Question, MarkedTag
from forum.tasks import topic_question_notification


class Command(NoArgsCommand):

    def handle_noargs(self, **options):

        for user in User.objects.filter(subscription_settings__notify_answers=True).exclude(
                facebook_access_token__isnull=True):

            # Obtain interesting tags query set
            marked = MarkedTag.objects.filter(user=user, reason='good')

            # Obtain interesting questions query set
            questions = Question.objects.filter(tags__id__in=marked.values_list('tag_id', flat=True).query)

            # Count interesting questions (last week)
            now = datetime.now()
            question_count = questions.filter(added_at__lt=now, added_at__gt=now - timedelta(days=7)).count()

            # Send notification
            if question_count:
                topic_question_notification.apply_async(countdown=10, args=(user.id, question_count))