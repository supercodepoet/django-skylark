Using Django CrunchyFrog
========================

CrunchyFrog is a Django app.  You can install it with pip::

    pip install django-crunchyfrog

Inside your settings.py add the following::

    INSTALLED_APPS = (
        'crunchyfrog',
    )

Developers
==========

Start out in the CrunchyFrog directory.

Let's bootstrap buildout::

    python bootstrap.py --distribute

Now run buildout::

    ./bin/buildout

It will take a bit, downloading all the dependencies it needs.  Once it's
finished try running the tests::

    ./bin/test

Building the documentation
==========================

Docs are in the :file:`docs` directory.  It was written using Sphinx.

To build the documentation::

    cd docs/
    make html

The Makefile should then build the html version and stick the output in the
:file:`docs/_build directory`.
