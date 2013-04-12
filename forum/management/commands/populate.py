# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from forum.models import *
from forum.actions import UserJoinsQuietly
import datetime
from random import choice


class Command(BaseCommand):

    def _create_user(self, username, email, date_joined, real_name, password, user_type):

        user = User.objects.get_or_create(username=username, email=email, date_joined=date_joined)
        print user
        if isinstance(user, tuple):
            user, created = user
        else:
            created = False

        if created:
            user.first_name, user.last_name = real_name.split()
            user.email_isvalid = True
            user.set_password(password)
            user.user_type = user_type
            user.save()
            UserJoinsQuietly(user=user).save()

        return user, created


    def handle(self, *args, **options):
        # First we create an educator and a cohort of students. (cohorts are classes of students)

        firstname = "John"
        lastname = "Educator"
        real_name = firstname+" "+lastname
        email = "example1@careervillage.org"
        username = "Educator1"
        password = "password"
        join_date = datetime.datetime(2012, 3, 31)
        user, user_created = self._create_user(username, email, join_date, real_name, password, 'educator')

        try:
            newcohort = Cohort.objects.get(name="ExampleClass", created_at="2013-03-31", kickoff_date="2013-03-31")
        except Cohort.DoesNotExist:
            newcohort = Cohort.objects.create(name="ExampleClass", created_at="2013-03-31", kickoff_date="2013-03-31")

        if user_created:
            newcohort.add_educator(username)

        # Then we create 3 students and post questions as them.
        # Then we create 3 students and post questions as them.
        # Then we create 3 students and post questions as them.

        firstname = "Samantha"
        lastname = "Student"
        real_name = firstname+" "+lastname
        email = "example2@careervillage.org"
        username = "Student1"
        password = "password"
        join_date = datetime.datetime(2012, 3, 31)
        user, created = self._create_user(username, email, join_date, real_name, password, 'student')
        if created:
            newcohort.add_student(username)

            NewQ = Question(title="How much money do lawyers make?", tagnames="money lawyer compensation", author=user, body="I am a senior in high school and I am looking into studying this field. I want to make sure that once I graduate and am able to find a job, that I will be able to have enough money to live a comfortable life.")
            NewQ.save()

            NewQ = Question(title="How do I become a stockbroker?", tagnames="finance power career-paths", author=user, body="I want to be a stockbroker. It looks pretty awesome on TV! How do I achieve my dream?")
            NewQ.save()

            NewQ = Question(title="Can I live in New York and survive in the arts?", tagnames="arts cities money", author=user, body="I want to be in the artistic scene. But I hear it is hard to make enough money. Will I starve?")
            NewQ.save()

        firstname = "Suzy"
        lastname = "Student"
        real_name = firstname+" "+lastname
        email = "example3@careervillage.org"
        username = "Student2"
        password = "password"
        join_date = datetime.datetime(2012, 3, 31)
        user, created = self._create_user(username, email, join_date, real_name, password, 'student')
        if created:
            newcohort.add_student(user.username)

            NewQ = Question(title="What does a typical day of a Therapist consist of?", tagnames="athletic therapy", author=user, body="Hi, I am a senior in high school and I was wondering, what is a typical day for a therapist?")
            NewQ.save()

            NewQ = Question(title="Entrepreneurship in Mechanical Engineering?", tagnames="business engineering mechanical-engineering", author=user, body="Hello I am a senior in high school and was interested in Mechanical Engineering, but at the entrepreneur/managing level, like making my own product and selling it someday. Does anybody know what it looks like to manage an organization or group of people who do Mechanical Engineering? Thanks.")
            NewQ.save()

            NewQ = Question(title="How much do criminal lawyers make in a year?", tagnames="lawyer", author=user, body="On average, how much do lawyers typically make?")
            NewQ.save()

        firstname = "Sarah"
        lastname = "Student"
        real_name = firstname+" "+lastname
        email = "example4@careervillage.org"
        username = "Student3"
        password = "password"
        join_date = datetime.datetime(2012, 3, 31)
        user, created = self._create_user(username, email, join_date, real_name, password, 'student')
        if created:
            newcohort.add_student(user.username)

            NewQ = Question(title="Which teacher make more money, private school teachers or public school teachers?", tagnames="teacher money career-paths school", author=user, body="I am a 10th grade student at Codman Academy and I would like to know which teacher makes more money.")
            NewQ.save()

            NewQ = Question(title="How many things do i have to major in to be an airplane engineer?", tagnames="mechanical-engineering engineering aerospace-engineering electrical-engineering", author=user, body="im a high school student who knows people in engineering airplanes and they have alot of money so how many things do i have to major in to get to where they are.")
            NewQ.save()

            NewQ = Question(title="I want a career in travelling", tagnames="investigator scene crime", author=user, body="I know that people who work in this field tend to work irregular hours so the amount that certain individuals are paid may vary. Some work very few hours whereas others work many hours including evenings and weekends. I would not mind working a lot of hours as long as i get paid a decent amount of money.")
            NewQ.save()

        # Then we create 3 professionals and post answers as them.
        # Then we create 3 professionals and post answers as them.
        # Then we create 3 professionals and post answers as them.

        firstname = "Jamie"
        lastname = "Professional"
        real_name = firstname+" "+lastname
        email = "example5@careervillage.org"
        username = "Professional1"
        password = "password"
        join_date = datetime.datetime(2012, 3, 31)
        user, created = self._create_user(username, email, join_date, real_name, password, 'professional')
        if created:
            question=choice(Question.objects.all())
            NewA = Answer(body='Here is a placeholder with the answer to your question. I think the answer is yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada.', author=user, parent=question)
            NewA.save()

            question=choice(Question.objects.all())
            NewA = Answer(body='Here is a placeholder with the answer to your question. I think the answer is yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada.', author=user, parent=question)
            NewA.save()

            question=choice(Question.objects.all())
            NewA = Answer(body='Here is a placeholder with the answer to your question. I think the answer is yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada.', author=user, parent=question)
            NewA.save()

            question=choice(Question.objects.all())
            NewA = Answer(body='Here is a placeholder with the answer to your question. I think the answer is yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada.', author=user, parent=question)
            NewA.save()

        firstname = "Lex"
        lastname = "Professional"
        real_name = firstname+" "+lastname
        email = "example6@careervillage.org"
        username = "Professional2"
        password = "password"
        join_date = datetime.datetime(2012, 3, 31)
        user, created = self._create_user(username, email, join_date, real_name, password, 'professional')
        if created:
            question=choice(Question.objects.all())
            NewA = Answer(body='Here is a placeholder with the answer to your question. I think the answer is yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada.', author=user, parent=question)
            NewA.save()

            question=choice(Question.objects.all())
            NewA = Answer(body='Here is a placeholder with the answer to your question. I think the answer is yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada.', author=user, parent=question)
            NewA.save()

            question=choice(Question.objects.all())
            NewA = Answer(body='Here is a placeholder with the answer to your question. I think the answer is yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada.', author=user, parent=question)
            NewA.save()

            question=choice(Question.objects.all())
            NewA = Answer(body='Here is a placeholder with the answer to your question. I think the answer is yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada.', author=user, parent=question)
            NewA.save()

        firstname = "Sam"
        lastname = "Professional"
        real_name = firstname+" "+lastname
        email = "example6@careervillage.org"
        username = "Professional3"
        password = "password"
        join_date = datetime.datetime(2012, 3, 31)
        user, created = self._create_user(username, email, join_date, real_name, password, 'professional')
        if created:
            question=choice(Question.objects.all())
            NewA = Answer(body='Here is a placeholder with the answer to your question. I think the answer is yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada.', author=user, parent=question)
            NewA.save()

            question=choice(Question.objects.all())
            NewA = Answer(body='Here is a placeholder with the answer to your question. I think the answer is yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada.', author=user, parent=question)
            NewA.save()

            question=choice(Question.objects.all())
            NewA = Answer(body='Here is a placeholder with the answer to your question. I think the answer is yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada.', author=user, parent=question)
            NewA.save()

            question=choice(Question.objects.all())
            NewA = Answer(body='Here is a placeholder with the answer to your question. I think the answer is yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada yada.', author=user, parent=question)
            NewA.save()



