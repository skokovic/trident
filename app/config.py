import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'specijalni kljuc'

    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)
    id = os.environ.get('FACEBOOK_ID')
    secret = os.environ.get('FACEBOOK_SECRET')
    OAUTH_CREDENTIALS = {'facebook': {'id': id,
                                      'secret': secret}
                         }
    SECURITY_POST_LOGIN = '/profile'

