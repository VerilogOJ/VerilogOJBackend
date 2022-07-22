from .base import *

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': [

        # temporarily enable this to test api in django built-in coreapi docs
        # since SessionAuthentication checks for scrf_token, which the docs fail to 
        # give
        # TODO: comment on production
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'judge.judger_auth.JudgerAuthentication',
    ],
}


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'xlb=+p_mb+z&=+4&++liz*ka_jc!ml8w#m+0jfbs0_8@4)s_w+'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

