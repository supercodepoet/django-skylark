====================
404 and 500 handlers
====================

Django provides a way for you to specify handlers for 404 and 500 errors once
``DEBUG`` has been turned ``False``.

Here is an example of how you accomplish this in Django.

:file:`urls.py` ::

    from django.conf.urls.defaults import *
    from dummyapp.views import index

    from skylark.views.generic import *

    handler404 = 'myproject.views.handle404'
    handler500 = 'myproject.views.handle500'

    urlpatterns = patterns('',
        (r'^$', 'dummyapp.views.index'),
    )

As of Django 1.1 (this changed around the release of 1.2) you had to use a
string here instead of a callable.  However we workaround this to make the
following possible.

Using Django Skylark to render 404 and 500 pages
---------------------------------------------

.. warning:: You have to be careful.  We are dealing with error pages, typically
    seen when something goes wrong in the case of a 500.  You need to test these
    before you just let them ride.  If you have an error within your YAML or
    your template these can escape into the ether and you will not know why.

Use the following methods to alter the handlers.

.. method:: render_404_from_yaml(yaml_filename)
    
    For, you guessed it, 404 handlers.

.. method:: render_500_from_yaml(yaml_filename)

    For, uh yup, 500 handlers

An example ::

    from django.conf.urls.defaults import *
    from dummyapp.views import index

    from skylark.views.generic import *

    handler404 = render_404_from_yaml('dummyapp/handler/404.yaml')
    handler500 = render_500_from_yaml('dummyapp/handler/500.yaml')

    urlpatterns = patterns('',
        (r'^$', 'dummyapp.views.index'),
    )
