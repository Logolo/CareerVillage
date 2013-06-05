from celery import task
from forum.actions.facebook import NewQuestion

@task()
def new_question(id, message=None):
    from forum.models import Question
    question = Question.objects.get(id=id)
    NewQuestion(question.user, question, message).publish()