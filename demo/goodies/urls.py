from django.conf.urls.defaults import *
from crunchyfrog.ribt import test_registry

import views

urlpatterns = patterns('',
    (r'^list$', views.list),
)

