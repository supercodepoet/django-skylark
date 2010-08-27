========================================
Deploying Django Skylark into production
========================================

Deployment plans
----------------

Django Skylark manages all of the media files for you, this you probably have
figured out by now.  What you probably don't know is that you can tell
Django Skylark how you want it to behave.

Why have different methods of handling media?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Each ``<script src="?"></script>`` you list in you HTML has to make a request
and get a response from the server.  If you have a big application, this is
inefficient.  You also include a lot of whitespace and comments in Javascript
and CSS code.  It can create performance problems, and waste money (think
bandwidth costs).

Read this for a good explanation:
http://developer.yahoo.net/blog/archives/2007/07/high_performanc_8.html

By default, it will put ``<script>``, ``<link>``, and other tags into the HTML
exactly how you describe them in the YAML.  This is great for debugging, but
once you get ready to deploy t


What's the default
~~~~~~~~~~~~~~~~~~

If we can't find a deployment plan, we use :class:`SeparateEverything` by
default.

Making your deployment plan
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create :file:`mediadeploy.py` in the same directory your :file:`settings.py` is
in.

A deployment plan look like this ::

    from skylark import plans
    from django.conf import settings

    if settings.DEBUG:
        default = plans.SeparateEverything
    else:
        default = plans.ReusableFiles

We'll go over what each plan does, but for now this is a good start.  Copy this
verbatim and keep on rollin.

How will the deployment plan be processed?

    #. Django Skylark will look for a :file:`mediadeploy.py` file (this can be
       changed with :attr:`SKYLARK_PLANS`)
    #. If uses the value of ``default`` as the plan you wish to use. (this can
       be changed with :attr:`SKYLARK_PLANS_DEFAULT`)
    #. It creates an instance of the plan to use as it throws media around.

SeparateEverything
~~~~~~~~~~~~~~~~~~

.. module:: plans.SeparateEverything

.. note:: This is the default plan if you don't have a deployment plan created

This plan takes your YAML files and outputs them into the HTML without any
modification at all.  It will not minify any of your Javascript or CSS.

This is good for debugging and developing but not for production.

.. warning:: It's recommended that you do not use this in production environments

ReusableFiles
~~~~~~~~~~~~~

.. module:: plans.ReusableFiles

This plan takes any :attr:`uses` blocks from you YAML and combines and minifies
them into one file.  If you haven't used :attr:`uses` it doesn't make much sense
to use this plan.  But if you site has gotten sufficiently large enough you
probably are.

FewestFiles
~~~~~~~~~~~

.. module:: plans.FewestFiles

This plan rolls up as much as possible into one file.  It can be handy for pages
that are visited frequently and can benefit from caching their Javascript and
CSS.

.. warning:: It may not be the best idea to use this site-wide as every page will
   have a separate Javascript and CSS file.  This is mainly in place to support
   a future feature of Django Skylark where you can specify plans be applied to
   specific views.

Options
-------

The deployment plans can be altered with options.

``minify_javascript``
~~~~~~~~~~~~~~~~~~~~~

Default: ``True``

When rolling up Javascript, should we minify it? ::

    plan_options(minify_javascript=True) 
