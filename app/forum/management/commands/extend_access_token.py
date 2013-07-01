from django.utils.timezone import now
from datetime import timedelta
from django.core.management.base import BaseCommand
from forum.actions.facebook import Graph
from forum.models import User


class Command(BaseCommand):

    def handle(self, *args, **options):
        for user in User.objects.filter(facebook_access_token_expires_on__lt=now() + timedelta(days=2)):
            user.facebook_access_token = Graph.extend_access_token(user.facebook_access_token)
            user.save()

