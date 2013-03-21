from django.test import TestCase
from django.test.testcases import TransactionTestCase
from forum.models.user import User, DEFAULT_USER_TYPE
from forum.models.meta import Badge
from forum.actions import AskAction, DeleteAction, AnswerAction, CommentAction
from forum.forms import AskForm, AnswerForm

# This test file was written to fix the cohort question display bug

class MetaTestCase(TransactionTestCase):
    '''
    Checks that count methods return the proper values as posts are
     added and deleted.
    '''

    def setUp(self):
        pass


    def test_badges_work(self):
        badge = Badge.objects.all()
        print badge

