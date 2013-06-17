from django.test import TestCase
from forum.models.question import Question
from forum.models.user import User
from forum.actions import ReferralAction


class ReferralTestCase(TestCase):
    '''
    Ensures that referring increases the referral_count of the
    referring user.
    '''

    def setUp(self):
        self.referred_user = User(username="a")
        self.referred_user.save()
        self.referred_by = User(username="b")
        self.referred_by.save()
        self.referred_by.prop.referral_count = 0
        self.question = Question(author=self.referred_by)
        self.question.save()

    def test_referral(self):
        self.assertEqual(self.referred_by.referrals.count(), 0)
        self.assertEqual(self.referred_by.prop.referral_count, 0)
        referral_action = ReferralAction(user=self.referred_by).save(dict(referred_user=self.referred_user))
        self.assertEqual(self.referred_by.referrals.count(), 1)
        self.assertEqual(self.referred_by.prop.referral_count, 1)

