from celery import task
from forum.actions.facebook import AskQuestionStory, NewAnswerStory, NewAwardStory, FollowTopicStory, AnswerNotification
from forum.models import Question, Answer, Award, User, Tag


@task()
def new_question(question_id, message=None):
    AskQuestionStory(Question.objects.get(id=question_id), message).publish()


@task()
def new_answer(answer_id, message=None):
    NewAnswerStory(Answer.objects.get(id=answer_id), message).publish()


@task()
def new_award(award_id):
    NewAwardStory(Award.objects.get(id=award_id)).publish()


@task()
def answer_notification(answer_id):
    AnswerNotification(Answer.objects.get(id=answer_id)).notify()


@task()
def follow_topic(user_id, topic_id):
    FollowTopicStory(User.objects.get(id=user_id), Tag.objects.get(id=topic_id)).publish()

