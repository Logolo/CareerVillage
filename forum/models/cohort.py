import datetime
from base import *

from django.utils.translation import ugettext as _

from forum import modules
from forum.models.user import User
from forum.models import Question

# NOTE: It is assumed that students will be added to cohorts upon joining
# the site and the Cohort functions reflect this. 


class Cohort(BaseModel):

    name = models.CharField(max_length=255, unique=True)
    educators = models.ManyToManyField('User', related_name='educator_of')
    students = models.ManyToManyField('User', related_name='student_of')
    created_at = models.DateTimeField(default=datetime.datetime.now, blank=True, null=True)
    kickoff_date = models.DateTimeField(default=datetime.datetime.now, blank=True, null=True)

    class Meta:
        app_label = 'forum'

    def __unicode__(self):
        return u'%s' % self.name
    
    def add_student(self, students):
        if type(students) != type([]):
            self.students.add(User.objects.get(username=students))
        self.students.add(*User.objects.filter(username__in=students))
        
    def add_educator(self, educators):
        if type(educators) != type([]):
            self.educators.add(User.objects.get(username=educators))
        self.educators.add(*User.objects.filter(username__in=educators))

    @property
    def reputation(self):
        return sum([s.reputation for s in self.students.all()])
    
    #Reputation earned by students in cohort for last days
    def time_reputation(self, days=7):
        return sum([s.get_reputation_by_actions(days=days) for s in self.students.all()])

    #total student questions or number of students that asked questions
    #if sum=False
    def time_questions(self, days=7, sum=True):
        question_count = 0
        for student in self.students.all():
            q_count = student.get_question_count(days=days)
            if (q_count > 0):
                question_count += sum and q_count or 1
        return question_count

    def time_answers_received(self, days=7):
        answers_received_count = 0
        today = datetime.date.today()
        for student in self.students.all():
            qs = Question.objects.filter_state(deleted=False).filter(author=student)
            for q in qs:
                for a in q.answers:
                    if (a.last_activity.date() >= (datetime.date.today() - datetime.timedelta(days=days))):
                        answers_received_count += 1
        return answers_received_count

    def time_pageviews(self, days=7):
        return 'n/a'

    def time_comments(self, days=7):
        return sum([s.get_comment_count(days=days) for s in self.students.all()])

    #students who have logged in within the given number of days
    def time_logins(self, days=7):
        logged_in_count = 0
        for student in self.students.all():
            if (student.get_logged_in_within(days=days)):
                logged_in_count += 1
        return logged_in_count
    
    #student information since the beginning 
    def student_details_all(self):
        detail_list = []
        for student in self.students.all():
            detail={}
            detail['student']=student
            detail['questions']=student.actions.filter(canceled=False, action_type='ask').count()
            detail['answers']=student.actions.filter(canceled=False, action_type='answer').count()
            detail['points']=student.reputation
            detail_list.append(detail)
        return detail_list

    #days=ALL not yet implemented
    def student_details(self, days=7):
        """
        Returns a dictionary of aggregate and individual student data for a
         given number of days
        """
        students = self.students.all()
        total, individuals = {}, []

        total['points'] = self.time_reputation(days=days)
        total['questions'] = self.time_questions(days=days)
        total['answers_received'] = self.time_answers_received(days=days)
        total['pageviews'] = self.time_pageviews(days=days)
        total['comments'] = self.time_comments(days=days)
        login_data = self.time_logins(days=days)
        #NOTE: this is taken to mean 'students who logged in at least once'
        total['logins'] = login_data
        total['login_percent'] = "%.2f" % (login_data * 100.0 / students.count())

        for student in students:
            student_detail={}
            student_detail['student']=student
            student_detail['questions']=student.get_question_count(days=days)
            student_detail['answers']=student.get_answer_count(days=days)
            student_detail['points']=student.get_reputation_by_actions(days=days)
            answers_received_count = 0
            today = datetime.date.today()
            qs = Question.objects.filter_state(deleted=False).filter(author=student)
            for q in qs:
                for a in q.answers:
                    if (a.last_activity.date() >= (datetime.date.today() - datetime.timedelta(days=days))):
                        answers_received_count += 1
            student_detail['answers_received']=answers_received_count
            individuals.append(student_detail)
        details = {'totals' : total, 'individuals' : individuals}
        return details
