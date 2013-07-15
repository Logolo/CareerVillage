from celery import task
from forum.actions.facebook import AskQuestionStory, LikeQuestionStory, AwardBadgeStory,\
    AnswerQuestionNotification, AnswerQuestionStory, LikeAnswerStory, InterestTopicStory,\
    GetPointStory, ReachPointStory, TopicQuestionNotification, AwardBadgeNotification
from forum.models import Question, Answer, Award, User, Tag


# Facebook stories

@task()
def facebook_like_question_story(user_id, question_id, message=None, app=None):
    LikeQuestionStory(User.objects.get(id=user_id),
                      Question.objects.get(id=question_id), app=app).publish()


@task()
def facebook_like_answer_story(user_id, answer_id, message=None, app=None):
    LikeAnswerStory(User.objects.get(id=user_id),
                    Answer.objects.get(id=answer_id), app=app).publish()


@task()
def facebook_ask_question_story(question_id, message=None, app=None):
    AskQuestionStory(Question.objects.get(id=question_id), message, app=app).publish()


@task()
def facebook_answer_question_story(answer_id, message=None, app=None):
    AnswerQuestionStory(Answer.objects.get(id=answer_id), message, app=app).publish()


@task()
def facebook_award_badge_story(award_id, app=None):
    AwardBadgeStory(Award.objects.get(id=award_id), app=app).publish()


@task()
def facebook_interest_topic_story(user_id, topic_id, app=None):
    InterestTopicStory(User.objects.get(id=user_id), Tag.objects.get(id=topic_id), app=app).publish()


@task()
def facebook_get_point_story(user_id, point_count, app=None):
    GetPointStory(User.objects.get(id=user_id), point_count, app=app).publish()


@task()
def facebook_reach_point_story(user_id, point_count, app=None):
    ReachPointStory(User.objects.get(id=user_id), point_count, app=app).publish()


# Facebook notifications

@task()
def facebook_answer_question_notification(answer_id, app=None):
    AnswerQuestionNotification(Answer.objects.get(id=answer_id), app=app).notify()


@task()
def facebook_topic_question_notification(user_id, question_count, app=None):
    TopicQuestionNotification(User.objects.get(id=user_id), question_count, app=app).notify()


@task()
def facebook_award_badge_notification(award_id, app=None):
    AwardBadgeNotification(Award.objects.get(id=award_id), app=app).notify()
