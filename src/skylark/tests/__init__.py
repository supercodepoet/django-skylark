import os
import shutil
from time import time
from django.http import HttpRequest
from django.core.management import setup_environ

import settings as settings_module
setup_environ(settings_module)
from django.conf import settings

projectdir = os.path.join(os.path.dirname(__file__))

cachedir = settings.SKYLARK_CACHE_ROOT


def exist(*filelist):
    for file in filelist:
        assert os.path.isfile(os.path.join(cachedir, file))


def get_one_file_in(path):
    started = time()
    while (time() - started < 3.0):
        for file in os.walk(path):
            files = file[2] # the third element is an array of files
            if files:
                return os.path.join(file[0], files[0])

    raise Exception, 'Could not find a file in %s' % path


def get_contents(filename):
    try:
        f = open(filename, 'r')

        content = f.read()
        f.close()

        return content
    except IOError:
        from pprint import PrettyPrinter
        pformat = PrettyPrinter(indent=4).pformat
        raise Exception('Could not file %s, options are\n%s' % (filename,
            pformat(os.listdir(os.path.dirname(filename)))))


def get_request_fixture():
    request = HttpRequest()
    request.path = '/'
    request.META = { 'REMOTE_ADDR': '127.0.0.1', 'SERVER_NAME': '127.0.0.1', 'SERVER_PORT': '8000' }
    return request


def setup():
    settings.DEBUG = True
    settings.SKYLARK_PLANS = 'mediadeploy'
    settings.SKYLARK_PLANS_DEFAULT = 'default'
    settings.SKYLARK_PLANS_ROLLUP_SALT = 'aaaaaaaaaaaaaaaa'
    settings.SKYLARK_ENABLE_TIDY = False


def teardown():
    # Remove everything but the addons
    skip = ['addon']
    try:
        for topdir in os.listdir(cachedir):
            if topdir in skip: continue
            shutil.rmtree(os.path.join(cachedir, topdir))
    except OSError:
        pass
