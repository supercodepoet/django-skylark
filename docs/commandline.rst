=======================================
Django Skylark's command line interface
=======================================

Preparing to use the command line interface
-------------------------------------------

Django Skylark has the ability to hook into the Django command line to help you
with some tasks.

You've probably used these built-in commands a lot.  Here are some examples ::

    python manage.py runserver
    python manage.py startproject myproject
    python manage.py syncdb

These are all commands within Django's management system.

To make sure you can run Django Skylark's, go through the following checklist:

- Make sure you have :doc:`installed Django Skylark</install>`
- Make sure you have listed ``skylark`` in ``INSTALLED_APPS``
- Make sure you can run ``python manage.py help`` and see ``skylarkpage``,
  ``skylarkclearcache``, ``skylarkcopymedia`` as options

Creating pages the easy way
---------------------------

With this command you need to know two things:

- The app name
- The new page name you want to create

To make sense of the page concept, think of them as equivalent to functions
within your view.

If you had a function within your view that was named ``goodies.views.list``
you would have a Django Skylark page named ``list``.

To create this ::

    python manage.py skylarkpage -a goodies -p list

It will walk you through the process, creating the templates directory if you
haven't done this already, and make the necessary directories and files that it
needs.

If you want to turn off the confirmation messages, you can add a ``-n`` or
``--noconfirm`` to your command. ::

    python manage.py skylarkpage -a goodies -p list -n
