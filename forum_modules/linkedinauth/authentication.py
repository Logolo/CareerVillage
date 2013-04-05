from consumer import OAuthAbstractAuthConsumer
from forum.authentication.base import ConsumerTemplateContext
import settings

class LinkedinAuthConsumer(OAuthAbstractAuthConsumer):
    def __init__(self):
        OAuthAbstractAuthConsumer.__init__(self,
            str(settings.LINKEDIN_CONSUMER_KEY),
            str(settings.LINKEDIN_CONSUMER_SECRET),
            "https://api.linkedin.com/uas/oauth2/accessToken",
            "https://www.linkedin.com/uas/oauth2/authorization",
        )

    def get_user_data(self, key):
        url = "https://api.linkedin.com/v1/people/~:(id,skills,interests,first-name,last-name,headline,industry,picture-url,location)"
        return self.fetch_data(key, url)

class LinkedinAuthContext(ConsumerTemplateContext):
    mode = 'NOICON' #CHANGED FROM BIGICON TO REMOVE FROM THE SIGNIN.HTML TEMPLATE
    type = 'DIRECT'
    weight = 150
    human_name = 'Linkedin'
    icon = '/media/images/openid/linkedin.png'