from django.test import TestCase
from forum.models.user import User, DEFAULT_USER_TYPE
from forum.actions import AskAction, DeleteAction, AnswerAction, CommentAction
from forum.forms import AskForm, AnswerForm

# This test file was written to fix the cohort question display bug

class StudentTestCase(TestCase):
    '''
    Checks that count methods return the proper values as posts are
     added and deleted.
    '''

    def setUp(self):
        self.student = User()
        self.student.save()


    def _ask_question(self):
        '''
        Creates a question via an AskForm and AskAction and associates that
        question with a user. Defaults to self.student
        '''
        ask_form = AskForm(data={ 'title': 'testingtesting',
                                  'text': 'texttexttexttext',
                                  'tags': 'dummytag'}, user=self.student)
        self.assertTrue(ask_form.is_valid(), msg="AskForm failed is_valid in _ask_question")

        ask_action = AskAction(user=self.student).save(data=ask_form.cleaned_data)
        question = ask_action.node
        return question

    def _answer_question(self, question):
        answer_form = AnswerForm({'text': 'texttexttexttexttext'}, user=self.student)
        self.assertTrue(answer_form.is_valid(), msg="AnswerForm failed is_valid in _answer_question")
        answer_action = AnswerAction(user=self.student).save(dict(question=question, **answer_form.cleaned_data))
        answer = answer_action.node
        return answer

    # comment on a post
    def _comment(self, post):
        comment = CommentAction(user=self.student).save(
            data=dict(text='texttexttexttexttext', parent=post)
        ).node
        return comment

    def _check_counts(self, questions, answers, comments):
        self.assertEqual(self.student.get_question_count(), questions)
        self.assertEqual(self.student.get_answer_count(), answers)
        self.assertEqual(self.student.get_comment_count(), comments)

    # Check that user get_x_count methods return the correct values
    # when we are adding new posts
    def test_counts_increase(self):

        # Make sure everything starts at zero
        self._check_counts(0, 0, 0)

        question = self._ask_question()
        self._check_counts(1, 0, 0)

        answer = self._answer_question(question)
        self._check_counts(1, 1, 0)

        comment = self._comment(answer)
        self._check_counts(1, 1, 1)

    # Check that user get_x_count methods return decreasing values as
    # posts are deleted
    def test_counts_decrease(self):

        def delete(node):
            DeleteAction(user=self.student, node=node).save()

        question = self._ask_question()
        answer = self._answer_question(question)
        comment = self._comment(answer)
        self._check_counts(1, 1, 1)

        delete(comment)
        self._check_counts(1, 1, 0)

        delete(answer)
        self._check_counts(1, 0, 0)

        delete(question)
        self._check_counts(0, 0, 0)


class UserTest(TestCase):


    def setUp(self):
        self.user = User(username='super')
        self.user.save()
        self.user.prop.user_type = None
        self.user.save()

    def test_user_type_default(self):
        self.assertEqual(self.user.user_type, DEFAULT_USER_TYPE)

    def test_user_type_permanence(self):
        self.user.user_type = "educator"
        u = User.objects.get(username='super')
        self.assertEqual(u.user_type, "educator")

    def test_gravatar(self):
        
        self.assert_(True)

    def test_save(self):
        self.assert_(True)

    def test_get_absolute_url(self):
        self.assert_(True)

    def test_get_messages(self):
        self.assert_(True)

    def test_delete_messages(self):
        self.assert_(True)

    def test_get_profile_url(self):
        self.assert_(True)

    def test_get_profile_link(self):
        self.assert_(True)

    def test_get_visible_answers(self):
        self.assert_(True)

    def test_get_vote_count_today(self):
        self.assert_(True)

    def test_get_reputation_by_upvoted_today(self):
        self.assert_(True)

    def test_get_flagged_items_count_today(self):
        self.assert_(True)

    def test_can_view_deleted_post(self):
        self.assert_(True)

    def test_can_vote_up(self):
        self.assert_(True)

    def test_can_vote_down(self):
        self.assert_(True)

    def test_can_flag_offensive(self):
        self.assert_(True)

    def test_can_view_offensive_flags(self):
        self.assert_(True)

    def test_can_comment(self):
        self.assert_(True)

    def test_can_like_comment(self):
        self.assert_(True)

    def test_can_edit_comment(self):
        self.assert_(True)

    def test_can_delete_comment(self):
        self.assert_(True)

    def test_can_accept_answer(self):
        self.assert_(True)

    def test_can_edit_post(self):
        self.assert_(True)

    def test_can_retag_questions(self):
        self.assert_(True)

    def test_can_close_question(self):
        self.assert_(True)

    def test_can_reopen_question(self):
        self.assert_(True)

    def test_can_delete_post(self):
        self.assert_(True)

    def test_can_upload_files(self):
        self.assert_(True)

