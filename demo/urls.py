from django.conf import settings
from django.conf.urls.defaults import *
from skylark import ribt

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

ribt.autodiscover()

urlpatterns = patterns('',
    # Example:
    (r'^testrunner/', include('skylark.urls.ribt')),
    (r'^goodies/', include('goodies.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )
