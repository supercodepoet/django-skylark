====================================
CrunchyFrog's command line interface
====================================

Preparing to use the command line interface
-------------------------------------------

CrunchyFrog has the ability to hook into the Django command line to help you
with some tasks.

You've probably used these built-in commands a lot.  Here are some examples ::

    python manage.py runserver
    python manage.py startproject myproject
    python manage.py syncdb

These are all commands within Django's management system.

To make sure you can run CrunchyFrog's, go through the following checklist:

- Make sure you have :doc:`installed Django CrunchyFrog</install>`
- Make sure you have listed ``crunchyfrog`` in ``INSTALLED_APPS``
- Make sure you can run ``python manage.py help`` and see ``crunchypage``,
  ``crunchyclearcache``, ``crunchycopymedia`` as options

Creating pages the easy way
---------------------------

With this command you need to know two things:

- The app name
- The new page name you want to create

To make sense of the page concept, think of them as equivalent to functions
within your view.

If you had a function within your view that was named ``goodies.views.list``
you would have a CrunchyFrog page named ``list``.

To create this ::

    python manage.py crunchypage -a goodies -p list

It will walk you through the process, creating the templates directory if you
haven't done this already, and make the necessary directories and files that it
needs.

If you want to turn off the confirmation messages, you can add a ``-n`` or
``--noconfirm`` to your command. ::

    python manage.py crunchypage -a goodies -p list -n

Clearing the cache for a specific view
--------------------------------------

Django CrunchyFrog caches all the files that you reference in the YAML files
into the folder that specify in ``MEDIA_ROOT``.  TODO: How to override this.

With this command you need two things:

TODO due to a bug, this isn't working just yet

Copying media manually
----------------------

Django CrunchyFrog automatically copies things into the cache for you.  But for
some reason, if you need to do this manuall we have an inteface for that.

You need to know:

- The location of the media file

Here's how you manually copy the files into the CrunchyFrog cache::

    python manage.py crunchycopymedia -f goodies/list/list.yaml

