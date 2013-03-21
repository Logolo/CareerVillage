from django.core.exceptions import ObjectDoesNotExist
from django.test import LiveServerTestCase
from forum.models.question import Question
from forum.models.user import User
from selenium.webdriver.firefox.webdriver import WebDriver as FirefoxWebDriver
from selenium.common.exceptions import NoSuchElementException
from django.core.urlresolvers import reverse
from forum.tests.utils import create_question
import time

class FunctionalTestCase(LiveServerTestCase):
    '''
    '''
    @classmethod
    def setUpClass(cls):
        cls.selenium = FirefoxWebDriver()
        super(FunctionalTestCase, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        super(FunctionalTestCase, cls).tearDownClass()
        cls.selenium.quit()

    def assertPageLoaded(self):
        try:
            self.selenium.find_element_by_xpath('//body')
        except NoSuchElementException:
            self.fail('Page did not load properly (body not found)')

    def setUp(self):
        admin = User(username="admin")
        admin.save()
        test_user = User(username="test_user1")
        test_user.set_password('password')
        test_user.save()
        self.user = test_user
        test_user2 = User(username="test_user2")
        test_user2.set_password('password')
        test_user2.save()

        self.user2 = test_user2

    def url(self, name=""):
        return self.live_server_url + reverse(name)

    def load_url(self, url):
        self.selenium.get(self.live_server_url + url)

    def load_page(self, url_name):
        self.selenium.get(self.url(url_name))

    def login(self, username='test_user1', password='password'):
        self.load_page('auth_signin')
        self.fill_form({
            'username' : username,
            'password' : password
        })
        self.selenium.find_element_by_name('blogin').click()



    def fill_form(self, data):
        for field in data:
            form_field = self.selenium.find_element_by_name(field)
            form_field.send_keys(data[field])

    def find_partial_link(self):
        pass

    def test_homepage_loads(self):
        self.selenium.get(self.live_server_url)
        self.assertIn("CareerVillage", self.selenium.title)

    def test_login(self):
        self.login()
        time.sleep(2)
        try:
            self.selenium.find_element_by_xpath("//a[contains(@href, 'test_user1')]")
        except NoSuchElementException:
            self.fail('Failed to find user profile link')

    def test_can_create_account(self):
        self.selenium.get(self.url('auth_local_register'))
        self.assertIn("New user signup", self.selenium.title)

        self.assertEqual(User.objects.filter(username="test_user").count(), 0)
        self.fill_form({
            'username' : 'test_user',
            'password1' : 'password',
            'password2' : 'password',
            'email' : 'email@email.com'
        })

        submit = self.selenium.find_element_by_name("bnewaccount")

        submit.click()

        time.sleep(4)

        self.assertEqual(User.objects.filter(username="test_user").count(), 1)


    def test_ask_question(self):
        self.login()
        self.load_page('ask')
        title_text = 'question_test_111'
        body_text = 'this is some dummy text for my question so that it doesnt get upset'
        tags = 'dummytag'
        time.sleep(2)
        self.fill_form({
            'title' : title_text,
            #'text' : body_text,
            'tags' : tags
        })
        self.selenium.find_element_by_id('editor').send_keys(body_text)
        self.selenium.find_element_by_name('ask').click()
        time.sleep(2)

        self.assertPageLoaded()
        self.assertIn(title_text, self.selenium.current_url,
            msg="question title not found in url")

        try:
            question = Question.objects.get(title=title_text)
        except ObjectDoesNotExist:
            self.fail('Question not found in database')

        self.assertIn(body_text, question.body)
        self.assertEqual(tags, question.tagnames)
        self.assertEqual(self.user.id, question.author.id)

    def test_answer_question(self):
        self.user.user_type = "professional"
        question = create_question(self.user2)
        self.login()
        self.load_url(question.get_absolute_url())
        answer_text = 'this is the answer to your question I hope it is useful'
        self.fill_form({'text' : answer_text})
        self.selenium.find_element_by_xpath("//form/input[contains(@class,'submit')]").click()
        time.sleep(2)
        self.assertPageLoaded()
        self.assertEqual(question.answer_count, 1)










#class FirefoxTestCase(FunctionalTestCase):
#    '''
#    '''
#    @classmethod
#    def setUpClass(cls):
#        cls.selenium = FirefoxWebDriver()
#        super(FunctionalTestCase, cls).setUpClass()
#
#class ChromeTestCase(FunctionalTestCase):
#    '''
#    '''
#    @classmethod
#    def setUpClass(cls):
#        cls.selenium = ChromeWebDriver()
#        super(FunctionalTestCase, cls).setUpClass()
