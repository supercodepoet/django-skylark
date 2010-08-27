===============
Getting started
===============

Setting up a Django project, app, and preparing to use Django Skylark
------------------------------------------------------------------

Let's make a new Django project.  Let's assume you've already setup Django and
you're somewhat familiar with how this works.  If you haven't you can head over
to `Django installation guide`_ and get a handle on this.

::
    
    django-admin.py startproject demo 

If we do a directory listing, you should see something like this::

    demo
    demo/__init__.py
    demo/manage.py
    demo/settings.py
    demo/urls.py

Let's change directories into our new project. ::

    cd demo

Great, we've got a Django project started.  Let's install Django Skylark.
    
.. include:: install.rst

Now edit ``settings.py`` to add the to the installed apps directory. ::

    INSTALLED_APPS = (
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.sites',
        'skylark',
    )

We also need to make some tweeks to the ``MEDIA_ROOT`` and ``MEDIA_URL`` ::

    # Absolute path to the directory that holds media.
    # Example: "/home/media/media.lawrence.com/"
    MEDIA_ROOT = os.path.join(os.path.dirname(__file__), 'sitemedia')

    # URL that handles the media served from MEDIA_ROOT. Make sure to use a
    # trailing slash if there is a path component (optional in other cases).
    # Examples: "http://media.lawrence.com", "http://example.com/media/"
    MEDIA_URL = 'http://127.0.0.1:8000/sitemedia/'

But, we are using the ``os`` module here, so go to the top of ``settings.py``
and add this ::

    import os

Let's make sure we can start up our development server. ::

    python manage.py runserver

You should see this if all goes well. ::

    Validating models...
    0 errors found

    Django version 1.1 beta 1, using settings 'demo.settings'
    Development server is running at http://127.0.0.1:8000/
    Quit the server with CONTROL-C.

Ok, it works.  Now quit by hitting CONTROL-C.  Let's create an app. ::

    python manage.py startapp goodies

Now add this to the installed apps.  Edit ``settings.py`` again. ::

    INSTALLED_APPS = (
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.sites',
        'skylark',
        'goodies',
    )

Now we're gonna use Django Skylark's command line interface to get us going. ::

    python manage.py skylarkpage -a goodies -p list

What this is going to do is create a page called list in the goodies
application.  Pages will generally match up with a function in your view.

So as this command runs, the output is helpful.  It tells you exactly what it's
doing. ::

    We've found your app but no templates directory.

    We can create this for you and continue from here if you like.
                                                           
    Create /Users/robmadole/Development/workbench/skylarktutorial/demo/goodies/templates (yes/no)? 

Tell it ``yes`` so it will create the missing templates directory. ::

    We're about to create these directories:

    ./goodies/templates/goodies/list/media
    ./goodies/templates/goodies/list/media/css
    ./goodies/templates/goodies/list/media/img
    ./goodies/templates/goodies/list/media/js
    ./goodies/templates/goodies/list/media/js/template

    And these files

    ./goodies/templates/goodies/list/media/css/screen.css
    ./goodies/templates/goodies/list/media/js/list.js

    Are you sure you want to do this (yes/no)? 

Tell it ``yes`` again.  Now we'll create a set of files and directories for
Django Skylark to use.

And as the last bit that Django Skylark does, it outputs an example views.py file
for you.

So let's use this.  Copy and paste that last part into ``goodies/views.py`` ::

    from django.http import HttpResponse
    from skylark.page import PageAssembly, RequestContext

    def list(request):
        c = RequestContext(request, {
            #'name': "value"
        })

        pa = PageAssembly('goodies/list/list.yaml', c)

        return pa.get_http_response()
                        
Great.  We've got our view, the last thing we need is to hook a url up to this.

Edit ``goodies/urls.py`` ::

    from django.conf.urls.defaults import *

    import views

    urlpatterns = patterns('',
        (r'^list$', views.list),
    )

Edit ``urls.py`` for the main project ::

    from django.conf.urls.defaults import *

    # Uncomment the next two lines to enable the admin:
    # from django.contrib import admin
    # admin.autodiscover()

    urlpatterns = patterns('',
        # Example:
        # (r'^demo/', include('demo.foo.urls')),

        # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
        # to INSTALLED_APPS to enable admin documentation:
        # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

        # Uncomment the next line to enable the admin:
        # (r'^admin/', include(admin.site.urls)),

        (r'^goodies/', include('goodies.urls')),
    )

Enabling our ``MEDIA_ROOT`` to work like it needs to, put this at the bottom of
``urls.py`` ::

    from django.conf import settings
    if settings.DEBUG:
        urlpatterns += patterns('',
            (r'^sitemedia/(?P<path>.*)$', 'django.views.static.serve', { 'document_root': settings.MEDIA_ROOT }),
        )

Let's kick off the development server again, and then open 'er up. ::

    python manage.py runserver

Open ``127.0.0.1:8000/goodies/list`` in your favorite browser.  You should see
something like this. ::

    Your page is working (using only the finest baby frogs, dew picked and flown in from Iraq)    

Now would be a great time to go onto the next section to dive a :doc:`little
deeper into Django Skylark</intro>`.

.. _Django installation guide: http://docs.djangoproject.com/en/dev/intro/install/
