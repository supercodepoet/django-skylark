import os
import shutil
from time import time
from django.http import HttpRequest, HttpResponse
from django.core.management import setup_environ

import settings as settings_module
setup_environ(settings_module)
from django.conf import settings

projectdir = os.path.join(os.path.dirname(__file__))

cachedir = settings.CRUNCHYFROG_CACHE_ROOT

def get_one_file_in(path):
    started = time()
    while (time() - started < 3.0):
        for file in os.walk(path):
            files = file[2] # the third element is an array of files
            if files:
                return os.path.join(file[0], files[0])

    raise Exception, 'Could not find a file in %s' % path

def get_contents(filename):
    f = open(filename, 'r')

    content = f.read()
    f.close()

    return content

def get_request_fixture():
    request = HttpRequest()
    request.path = '/'
    request.META = { 'REMOTE_ADDR': '127.0.0.1', 'SERVER_NAME': '127.0.0.1', 'SERVER_PORT': '8000' }
    return request

def setup():
    pass

def teardown():
    if os.path.isdir(cachedir):
        shutil.rmtree(cachedir)
