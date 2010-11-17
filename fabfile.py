from fabric.api import env, run, put, local, roles
import datetime

from pkginfo import version

env.hosts     = ['localbase.webfactional.com']
env.roledefs  = {'eggserver': ['localbase.webfactional.com']}
env.user      = 'localbase'
env.name_left = 'django-skylark'

@roles('eggserver')
def deploy():
    """Deploys Django Skylark to our eggs directory on Web Faction"""
    filename = '%s-%s.tar.gz' % (env.name_left, version,)

    local_filename  = 'dist/%s' % filename
    remote_filename = '/home/localbase/webapps/eggs/%s' % filename

    local('python setup.py sdist')

    put(local_filename, remote_filename)
