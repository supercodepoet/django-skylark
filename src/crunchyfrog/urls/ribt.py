from django.conf.urls.defaults import *
from crunchyfrog.views.testrunner import *

urlpatterns = patterns('',
    url(r'^$', testrunner, name='ribt-testrunner'),
    url(r'^subject/start$', subject_start, name='ribt-testrunner-subject-start'),
    url(r'^deinstrument$', deinstrument, name='ribt-testrunner-deinstrument'),
)
