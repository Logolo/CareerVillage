__author__ = 'ben'
import factory
from forum.models.user import User
from forum.models.question import Question


class UserFactory(factory.DjangoModelFactory):
    FACTORY_FOR = User
    username = 'test_user'
    password = factory.PostGenerationMethodCall('set_password',
                                                'default_password')

class QuestionFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Question
    author = factory.SubFactory(UserFactory)


