from django.utils.timezone import now
from datetime import timedelta
from django.core.management.base import BaseCommand
from forum.actions.facebook import Graph
from forum.models import User
from forum import settings


FACEBOOK_APP = settings.djsettings.FACEBOOK_APP


class Command(BaseCommand):

    def handle(self, *args, **options):
        for user in User.objects.filter(facebook_accounts__app=FACEBOOK_APP,
                                        facebook_accounts__isnull=False,
                                        facebook_accounts__access_token_expires_on__lt=now() + timedelta(days=2)):
            facebook_account = user.facebook_account
            facebook_account.access_token, facebook_account.access_token_expires_on = \
                Graph.extend_access_token(facebook_account.access_token)
            facebook_account.save()

