from celery import task
from forum.actions.facebook import AskQuestionStory, NewAnswerStory, AnswerNotification
from forum.models import Question, Answer


@task()
def new_question(question_id, message=None):
    AskQuestionStory(Question.objects.get(id=question_id), message).publish()


@task()
def new_answer(answer_id, message=None):
    NewAnswerStory(Answer.objects.get(id=answer_id), message).publish()


@task()
def answer_notification(answer_id):
    AnswerNotification(Answer.objects.get(id=answer_id)).notify()
