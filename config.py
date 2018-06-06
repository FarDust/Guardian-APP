import os
DEBUG = True
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
STATIC_DIR = os.path.join(BASE_DIR,'static')

## -- Face detect
FACE_CLASIFIER = 'haarcascade_frontalface_default.xml'

## -- wea_app --
THREADS_PER_PAGE = 2
CSRF_ENABLED = True
CSRF_SESSION_KEY = "<secret>"
DB = 'face-security'
KEYCOLLECTION = 'persistent'
SECURITY = ['allowed', 'disallowed', 'wanted']
SECURITY_LIST = next(
    open(os.path.join(BASE_DIR, 'static', 'list_id.secret'), 'r'))
    