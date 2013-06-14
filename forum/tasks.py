from celery import task
from forum.actions.facebook import AskQuestionStory, LikeQuestionStory, AwardBadgeStory,\
    AnswerQuestionNotification, AnswerQuestionStory, LikeAnswerStory, InterestTopicStory,\
    GetPointStory, ReachPointStory, TopicQuestionNotification, AwardBadgeNotification
from forum.models import Question, Answer, Award, User, Tag


# Facebook stories

@task()
def facebook_like_question_story(question_id, message=None):
    LikeQuestionStory(Question.objects.get(id=question_id), message).publish()


@task
def facebook_like_answer_story(answer_id, message=None):
    # TODO: Implement
    # LikeAnswerStory(Answer.objects.get(id=answer_id), message).publish()
    pass


@task()
def facebook_ask_question_story(question_id, message=None):
    AskQuestionStory(Question.objects.get(id=question_id), message).publish()


@task()
def facebook_answer_question_story(answer_id, message=None):
    AnswerQuestionStory(Answer.objects.get(id=answer_id), message).publish()


@task()
def facebook_award_badge_story(award_id):
    AwardBadgeStory(Award.objects.get(id=award_id)).publish()


@task()
def facebook_interest_topic_story(user_id, topic_id):
    InterestTopicStory(User.objects.get(id=user_id), Tag.objects.get(id=topic_id)).publish()


@task()
def facebook_get_point_story(user_id, point_count):
    GetPointStory(User.objects.get(id=user_id), point_count).publish()


@task()
def facebook_reach_point_story(user_id, point_count):
    ReachPointStory(User.objects.get(id=user_id), point_count).publish()


# Facebook notifications

@task()
def facebook_answer_question_notification(answer_id):
    AnswerQuestionNotification(Answer.objects.get(id=answer_id)).notify()


@task()
def facebook_topic_question_notification(user_id, question_count):
    TopicQuestionNotification(User.objects.get(id=user_id), question_count).notify()


@task()
def facebook_award_badge_notification(award_id):
    AwardBadgeNotification(Award.objects.get(id=award_id)).notify()
