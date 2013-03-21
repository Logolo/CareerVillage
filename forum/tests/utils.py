from forum.actions.node import AskAction, AnswerAction, CommentAction
from forum.forms.qanda import AskForm, AnswerForm

__author__ = 'ben'

def create_question(author):
    '''
    Creates a question via an AskForm and AskAction and associates that
    question with a user. Defaults to self.student
    '''
    ask_form = AskForm(data={ 'title': 'testingtesting',
                              'text': 'texttexttexttext',
                              'tags': 'dummytag'}, user=author)
    #self.assertTrue(ask_form.is_valid(), msg="AskForm failed is_valid in _ask_question")
    ask_form.is_valid()
    ask_action = AskAction(user=author).save(data=ask_form.cleaned_data)
    question = ask_action.node
    return question

def answer_question(self, question):
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
