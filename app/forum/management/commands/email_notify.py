from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.db.models import Q

from forum.utils.mail import send_template_email
from forum.models import User, Question
from forum import settings


def usage():
    print 'Usage:'
    print '    For daily notifications:'
    print '    ./manage.py email_notify daily'
    print
    print '    For weekly notifications:'
    print '    ./manage.py email_notify weekly'


class Command(BaseCommand):

    def handle(self, *args, **options):
        try:
            (notifications,) = args
        except ValueError:
            usage()
            return

        if notifications == 'daily':
            notifications_lookup = User.NOTIFICATIONS_DAILY
            notifications_timedelta = timedelta(days=1)
            notifications_template = 'notifications/email_notification_daily.html'

        elif notifications == 'weekly':
            notifications_lookup = User.NOTIFICATIONS_WEEKLY
            notifications_timedelta = timedelta(weeks=1)
            notifications_template = 'notifications/email_notification_weekly.html'

        else:
            usage()
            return

        q = Q(notifications=notifications_lookup)
        if settings.djsettings.DEFAULT_NOTIFICATIONS == notifications_lookup:
            q |= Q(notifications=None)

        # Send notifications
        for user in User.objects.filter(q):
            questions = Question.objects.exclude(author=user).filter_state(deleted=False).filter(
                added_at__gt=datetime.now() - notifications_timedelta,
                tags__id__in=user.tag_selections.filter(
                    reason='good').values_list('tag_id', flat=True).query).distinct().order_by('added_at')

            if questions:
                print 'Sending notification to %s with %d questions.' % (user, questions.count())

                send_template_email([user], notifications_template, {
                    'questions': questions,
                })

        print 'Finished.'
