from django.conf.urls.defaults import *
from skylark.views.testrunner import *

urlpatterns = patterns('',
    url(r'^$', testrunner, name='chirp-testrunner'),
    url(r'^subject/start$', subject_start, name='chirp-testrunner-subject-start'),
    url(r'^deinstrument$', deinstrument, name='chirp-testrunner-deinstrument'),
)
