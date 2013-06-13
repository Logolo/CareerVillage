from celery import task
from forum.actions.facebook import AskQuestionStory, LikeQuestionStory, AwardBadgeStory,\
    AnswerQuestionNotification, AnswerQuestionStory, LikeAnswerStory, InterestTopicStory, GetPointStory,\
    TopicQuestionNotification
from forum.models import Question, Answer, Award, User, Tag


@task()
def like_question_story(question_id, message=None):
    LikeQuestionStory(Question.objects.get(id=question_id), message).publish()


@task()
def ask_question_story(question_id, message=None):
    AskQuestionStory(Question.objects.get(id=question_id), message).publish()


@task()
def answer_question_story(answer_id, message=None):
    AnswerQuestionStory(Answer.objects.get(id=answer_id), message).publish()


@task()
def award_badge_story(award_id):
    AwardBadgeStory(Award.objects.get(id=award_id)).publish()


@task()
def interest_topic_story(user_id, topic_id):
    InterestTopicStory(User.objects.get(id=user_id), Tag.objects.get(id=topic_id)).publish()

@task()
def get_point_story(user_id, point_count):
    GetPointStory(User.objects.get(id=user_id), point_count).publish()


@task()
def answer_question_notification(answer_id):
    AnswerQuestionNotification(Answer.objects.get(id=answer_id)).notify()


@task()
def topic_question_notification(user_id, question_count):
    TopicQuestionNotification(User.objects.get(id=user_id), question_count).notify()
