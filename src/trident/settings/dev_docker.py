from trident.settings.dev import *  # NOQA (ignore all errors on this line)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'trident_dev',
        'USER': 'trident',
        'PASSWORD': 'password',
        'HOST': 'postgres',
        'PORT': 5432,
    }
}
