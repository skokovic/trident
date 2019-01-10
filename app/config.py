import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'specijalni kljuc'

    OAUTH_CREDENTIALS = {'facebook': {'id': '2131939550179056',
                                      'secret': '0ab305fcb28d960afae167435f7e5f00'}
                        }
    SECURITY_POST_LOGIN = '/profile'

