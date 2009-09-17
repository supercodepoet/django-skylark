from fabric.api import env, run, put, local, roles
import datetime

env.hosts     = ['localbase.webfactional.com']
env.roledefs  = {'eggserver': ['localbase.webfactional.com']}
env.user      = 'localbase'
env.name_left = 'django-crunchyfrog-0.1dev'

@roles('eggserver')
def deploy():
    """Deploys Django Crunchy Frog to our eggs directory on Web Faction"""
    today = datetime.date.today()
    filename = '%s-%s.tar.gz' % (env.name_left, today.strftime('%Y%m%d'),) 

    local_filename  = 'dist/%s' % filename
    remote_filename = '/home/localbase/webapps/eggs/%s' % filename

    local('python setup.py sdist')

    put(local_filename, remote_filename)
