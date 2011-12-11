import datetime
from base import *

from django.utils.translation import ugettext as _

from forum import modules
from forum.models.user import User

# NOTE: It is assumed that students will be added to cohorts upon joining
# the site and the Cohort functions reflect this. 

class Cohort(BaseModel):
    name            = models.CharField(max_length=255, unique=True)
    educators       = models.ManyToManyField('User', related_name='educator_of')
    students        = models.ManyToManyField('User', related_name='student_of')
    created_at      = models.DateTimeField(default=datetime.datetime.now, blank=True, null=True)
    kickoff_date    = models.DateTimeField(default=datetime.datetime.now, blank=True, null=True)

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
        return sum([s.exit(days=days) for s in self.students.all()])
    
    #(students who have asked questions, total students) for past days
    def time_questions(self, days=7):
        question_count = 0
        for student in self.students.all():
            if (student.get_question_count(days=days) > 0):
                question_count += 1
        return (question_count, self.students.count())

    #(students who have been online, total students) for past days
    def time_logins(self, days=7):
        logged_in_count = 0
        for student in self.students.all():
            if (student.get_logged_in_within(days=days)):
                logged_in_count += 1
        return (logged_in_count, self.students.count())
    
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
    
    #student information since days
    def student_details(self, days=7):
        detail_list = []
        for student in self.students.all():
            detail={}
            detail['student']=student
            detail['questions']=student.get_question_count(days=days)
            detail['answers']=student.get_answer_count(days=days)
            detail['points']=student.get_reputation_by_actions(days=days)
            detail_list.append(detail)
        return detail_list
