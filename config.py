import os
from dotenv import load_dotenv

DEBUG = True
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
STATIC_DIR = os.path.join(BASE_DIR,'static')
if '.env' in os.listdir(BASE_DIR):
    load_dotenv()

## -- Face detect
FACE_CLASIFIER = 'haarcascade_frontalface_default.xml'
SECURITY_LIST = os.getenv('FACE_API_LIST')
_KEY = os.getenv('FACE_API_KEY')
_URL = os.getenv('FACE_API_URL')

## -- Database
DB = 'face-security'
KEYCOLLECTION = 'persistent'
SECURITY = ['allowed', 'disallowed', 'wanted']

## -- wea_app --
THREADS_PER_PAGE = 2
CSRF_ENABLED = True
CSRF_SESSION_KEY = "<secret>"