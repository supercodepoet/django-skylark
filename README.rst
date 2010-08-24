Using CrunchyFrog
=================

CrunchyFrog is a Django app.  You can install it with setup tools::

    python setup.py install

Inside your settings.py add the following:

INSTALLED_APPS = (
    'crunchyfrog',
)

Developers
==========

Start out in the CrunchyFrog directory.

First, create a virtualenv that can be used to isolate development::

    virtualenv --no-site-packages env

Now source the activate script::

    source env/bin/activate

Let's bootstrap buildout::

    python bootstrap.py

Now run buildout::

    ./bin/buildout --distribute

It will take a bit, downloading all the dependencies it needs.  Once it's
finished try running the tests::

    ./bin/test-11 (for testing Django 1.1)
    ./bin/test-12 (for testing with Django 1.2)

Documentation
=============

Docs are in the docs/ directory.  It was written with Sphinx and rST
(Re-structured text).

To build the documentation::

    cd docs/
    make html

The Makefile should then build the html version and stick the output in the
docs/_build directory.
