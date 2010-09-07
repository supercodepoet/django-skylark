from django.conf.urls.defaults import *
from dummyapp.views import index

from skylark.views.generic import *
from skylark import chirp

chirp.autodiscover()

handler404 = render_404_from_yaml('dummyapp/handler/404.yaml')
handler500 = render_500_from_yaml('dummyapp/handler/500.yaml')

urlpatterns = patterns('',
    (r'^$', 'dummyapp.views.index'),
    (r'^badview$', 'dummyapp.views.badview'),
    (r'^planapp$', 'planapp.views.index'),
)
