__author__ = 'ben'
from django.test import TestCase
from forum.models.cohort import Cohort
from forum.models.user import User
from forum.actions import AskAction, DeleteAction, AnswerAction
from forum.forms import AskForm, AnswerForm
from forum.models.tests.test_user import StudentTestCase

# This test file was written to fix the cohort question display bug

class CohortCountTest(StudentTestCase):
    '''
    Ensures that cohorts get counts correctly, especially after deletions

    Inherits count tests from StudentTestCase
    '''

    def setUp(self):
        super(CohortCountTest, self).setUp()
        self.cohort = Cohort()
        self.cohort.save()
        self.cohort.add_student([self.student])
        self.cohort.save()

    def _check_counts(self, questions, answers, comments):
        student_details = self.cohort.student_details()
        individual_data = student_details['individuals'][0]
        self.assertEqual(individual_data['questions'], questions)
        self.assertEqual(individual_data['answers'], answers)

        totals_data = student_details['totals']
        self.assertEqual(totals_data['questions'], questions)
        self.assertEqual(totals_data['comments'], comments)

    # (inherited)
    # Checks that cohorts student_details function will return the correct
    # number of posts as posts are added
    # def test_counts_increase(self):

    # (inherited)
    # Checks that cohorts student_details function will return the correct
    # number of posts as posts are deleted
    # def test_counts_decrease(self):


