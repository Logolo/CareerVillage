from celery import task
from forum.actions.facebook import AskQuestionStory, LikeQuestionStory, AnswerNotification
from forum.models import Question, Answer


@task()
def like_question_story(question_id, message=None):
    LikeQuestionStory(Question.objects.get(id=question_id), message).publish()


@task()
def ask_question_story(question_id, message=None):
    AskQuestionStory(Question.objects.get(id=question_id), message).publish()


@task()
def answer_notification(answer_id):
    AnswerNotification(Answer.objects.get(id=answer_id)).notify()
