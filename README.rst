What is this?
=============

Web development can be a pain.  HTML, CSS, Javascript, DOM; it's a few inches
shy of bamboo under your fingernails.  If you have a large application with a
few people working on it can get even worse.

Django Skylark attempts to make some of this better by:

    * Letting you describe your pages and something else assemble it
    * Managing your media
    * Providing a thin Javascript framework for those that don't need magic
    
Using Django Skylark
====================

Django Skylark is a Django app.  You can install it with pip::

    pip install django-skylark

Inside your settings.py add the following::

    INSTALLED_APPS = (
        'skylark',
    )

Documentation
=============

You can `view it online <http://packages.python.org/django-skylark/?>`_.

Or run these commands to build it locally ::

    python bootstrap.py --distribute
    ./bin/buildout
    cd docs
    make html; open _build/html/index.html
