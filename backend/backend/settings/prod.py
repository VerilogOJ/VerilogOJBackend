from .base import *

import socket

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
}

 #SECURITY WARNING: keep the secret key used in production secret!
if 'VERILOG_OJ_SECRET_KEY' not in os.environ:
    raise Exception("Verilog OJ should have VERILOG_OJ_SECRET_KEY passed by envvars")

SECRET_KEY = os.environ['VERILOG_OJ_SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Hmm, used for production debugging..
if 'VERILOG_OJ_PROD_DEBUG' in os.environ:
    DEBUG = True

if 'VERILOG_OJ_PUBLIC_HOST' not in os.environ:
    raise Exception("Verilog OJ should have VERILOG_OJ_PUBLIC_HOST passed by envvars")

ALLOWED_HOSTS = list(set([
    '127.0.0.1',
    'localhost',
    'backend',      # reference by hostname, used by judgeworker
    os.environ['VERILOG_OJ_PUBLIC_HOST']
]))

