from datetime import datetime, timedelta

from django.core.management.base import NoArgsCommand
from django.db.models import Q

from forum.models import User, Question, MarkedTag
from forum.tasks import facebook_topic_question_notification


class Command(NoArgsCommand):

    def handle_noargs(self, **options):

        for user in User.objects.filter(
                properties__key='facebook_topic_question_notification', properties__value=True).exclude(
                        Q(facebook_access_token__isnull=True) | Q(facebook_uid__isnull=True)):

            # Obtain interesting tags query set
            marked = MarkedTag.objects.filter(user=user, reason='good')

            # Obtain interesting questions query set
            questions = Question.objects.filter(tags__id__in=marked.values_list('tag_id', flat=True).query).distinct()

            # Count interesting questions (last week)
            now = datetime.now()
            question_count = questions.filter(added_at__lt=now, added_at__gt=now - timedelta(days=7)).count()

            # Send notification
            if question_count:
                facebook_topic_question_notification.apply_async(countdown=10, args=(user.id, question_count))
