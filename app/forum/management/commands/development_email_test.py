from optparse import make_option

from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType

from forum.models import User, Question, Answer
from forum.utils.mail import send_template_email


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--recipient', action='store', dest='recipient', help='Specify a recipient.', type='string'),
    )

    def handle(self, *args, **options):
        try:
            content_type, object_id = args
        except ValueError:
            print 'Usage:'
            print '    manage.py development_email_test [app_label].[model] [id] --recipient=[recipient]'
            print
            print 'Recipient can be a user id, user email, or one of the following:'
            print '    students, educators, professionals, all'
            print
            print 'Example:'
            print '    manage.py development_email_test forum.question 1 --recipient=1'
            print '    manage.py development_email_test forum.question 1 --recipient=user@domain.com'
            print '    manage.py development_email_test forum.answer 1 --recipient=all'
            print '    manage.py development_email_test forum.answer 1 --recipient=students'
            print '    manage.py development_email_test forum.question 1 --recipient=educators'
            print '    manage.py development_email_test forum.question 1 --recipient=professionals'
            return

        # Get content type
        try:
            app_label, model = content_type.split('.')
            content_type = ContentType.objects.get(app_label=app_label, model=model)
        except ValueError, ContentType.DoesNotExist:
            print 'Content type not found.'
            return

        # Get object
        model = content_type.model_class()
        try:
            obj = model.objects.get(id=object_id)
        except model.DoesNotExist:
            print 'Object not found.'
            return

        # Get recipients
        recipient = options.get('recipient')
        if recipient:
            if '@' in recipient:
                recipients = User.objects.filter(email=recipient)
            elif recipient == 'all':
                recipients = User.objects.all()
            elif recipient == 'students':
                recipients = User.objects.filter(type='S')
            elif recipient == 'educators':
                recipients = User.objects.filter(type='E')
            elif recipient == 'professionals':
                recipients = User.objects.filter(type='P')
            else:
                try:
                    recipients = [User.objects.get(id=recipient)]
                except User.DoesNotExist:
                    recipients = []
        else:
            print 'Must specify a recipient.'
            return

        # Finish if there are no recipients
        if not recipients:
            print 'No recipients found.'
            return

        # Show number of recipients
        print '%d recipients.' % len(recipients) if type(recipients) == list else recipients.count()
        print

        # Send "new question" message
        if isinstance(obj, Question):
            print 'Sending new question...'
            send_template_email(recipients, 'notifications/newquestion.html', {'question': obj})

        # Send "new answer" message
        elif isinstance(obj, Answer):
            print 'Sending new answer...'
            send_template_email(recipients, 'notifications/newanswer.html', {'answer': obj})

        # Nothing to do
        else:
            print 'Nothing to do.'

        print 'Finished.'
