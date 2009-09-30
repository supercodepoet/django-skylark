from django.conf.urls.defaults import *
from dummyapp.views import index
import crunchyfrog

urlpatterns = patterns('',
    (r'^cfmedia/', crunchyfrog.urls),
    (r'^$', 'dummyapp.views.index')
)
