from django.test import TestCase
from forum.models.tag import Tag, MarkedTag
from forum.models.user import User


class MarkingTagsTest(TestCase):
    '''
    Tests that marking tags as interesting has the current effect on users
    '''

    def setUp(self):

        self.student = User(username='super')
        self.student.set_password('secret')
        self.student.save()
        self.client.login(username='super', password='secret')
        self.tag = Tag.objects.create(name="testtag", created_by = self.student)

    def _check_tag_url(self, name):
        '''
        Checks that trying to view a tag page does not throw errors
        '''
        response = self.client.get('/tags/%s/' % name, follow=True)
        self.assertEqual(response.status_code, 200)

    def _student_tag_count(self):
        student_tags = MarkedTag.objects.filter(user=self.student, reason='good')
        return student_tags.count()

    def _test_following_tag(self, tag_name):
        '''
        Makes sure that marking tags as interesting causes the user to follow
        them and that the tag pages are error free
        '''
        self.assertEquals(self._student_tag_count(), 0)

        self.client.post('/mark-tag/interesting/%s/' % tag_name, follow=True)

        # If a tag is added the count should increment
        self.assertEquals(self._student_tag_count(), 1)

        # Make sure it is the correct tag
        student_tags = MarkedTag.objects.filter(user=self.student, reason='good')
        student_tag = student_tags.all()[0].tag
        self.assertEqual(student_tag.name, tag_name)

        # Make sure the tag page isn't broken
        self._check_tag_url(tag_name)

    def test_mark_existing_tag(self):
        self._test_following_tag(self.tag.name)

    def test_mark_nonexisting_tag(self):
        tag_name = 'tagtagtag'
        self._test_following_tag(tag_name=tag_name)

