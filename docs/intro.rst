===================================
Introduction to Django CrunchyFrog
===================================

.. epigraph::

    If we took the bones out it wouldn't be crunchy would it?

    -- Mr. Milton

Make web development easier
---------------------------
CrunchyFrog is a more structured, conventional way to produce web applications
that are what we typically consider Web 2.0.

It's not Flex_, Sproutcore_, or Cappuccino_.  Instead it's somewhere in between
those tools and stringing together Javascript, HTML, CSS, and images.

The intent is to make web development easier.  To simplify the things we do all
the time and to prevent the spaghetti code that typically somes about when you
try and create Web 2.0 applications from scratch.

Page assemblies
---------------

A common problem with developing Web 2.0 applications is you have a lot of
Javascript, CSS, and HTML files that have to be strung together to make the app
function.  This can get tedious.

How do we make this easier?
---------------------------

Here's an example of a PageAssembly::

    from django.http import HttpResponse
    from crunchyfrog.page import PageAssembly, RequestContext

    def list(request):
        c = RequestContext(request, {
            'confection': "Ram's bladder cup"
        })

        pa = PageAssembly('goodies/parts.yaml', c)

        return pa.get_http_response()

Let's look at ``goodies/list/list.yaml`` ::

    body: goodies/list/list.html
    title: Goodies

Ok, so we are pointing to a file that represents the body of our document.

What does ``goodies/list/list.html`` look like::

    <body>
        <h1>Whizzo Chocolates</h1>

        <p>My favorite is {{ confection }}</p>
    </body>

That's all we have so far.  Notice that we don't have a normal HTML page here.
There is no doctype, no ``<html>`` tag, it's just the good stuff: the ``<body>`` tag.

Now CrunchyFrog does it's thing.  It takes the bits you've assembled and is
going to render the page for you.

The HTML that this will create looks something like this::

    <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
    <html lang="en">
        <head>
            <title>Goodies</title>
        </head>

        <body>
            <h1>Whizzo Chocolates</h1>

            <p>My favorite is Ram&#39;s bladder cup</p>
        </body>
    </html>

Now that's not super-impressive, you could have written another template to
represent the shell of the page and utilized Django {% extend %} template tag
to make the same thing happen.  And really, what benefit did the YAML file give
you?  Well, none yet.  But let's march on, it will get more interesting.

Adding some assets (like Javascript or CSS)
-------------------------------------------

You can't have a Web 2.0 site without Javascript.  So we need to include jQuery.

The typical pattern to do this is that you'd create a directory off of your
MEDIA_ROOT and copy jQuery there.  Then you have to add the
``django.core.context_processors.media`` to your ``TEMPLATE_CONTEXT_PROCESSORS`` so you
can then use ``MEDIA_URL`` in your HTML pages.  CrunchyFrog has a different way.::

    body: goodies/list/list.html
    title: Goodies

    js:
        - url: {{ MEDIA_URL }}js/jquery.js

.. note:: You don't need to mess with TEMPLATE_CONTEXT_PROCESSORS, CrunchyFrog will take care
          of this for you

That makes it a bit easier.  We let the page assembly handle where to put the
script tag.  So now our HTML looks like this.::

    <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
    <html lang="en">
        <head>
            <title>Goodies</title>
            <script type="text/javascript" src="http://localhost:8000/site_media/js/jquery.js"></script>
        </head>

        <body>
            <h1>Whizzo Chocolates</h1>

            <p>My favorite is Ram&#39;s bladder cup</p>
        </body>
    </html>

Great.  We have jQuery now.  And we didn't have to dance with the Django
Template processors.  (Because CrunchyFrog worried about the ``MEDIA_URL`` for us
automatically.)

But this isn't doing anything.  We have included jQuery, but it's just sitting
there.  Let's make a Javascript file and do something.

Before we do though, let's take a quick look at our template directory
structure.  So far we have the following::

    ./templates/goodies/list/list.yaml
    ./templates/goodies/list/list.html

.. note:: This is where we start to leverage the power of Django Template loaders
    to help us find files

We are going to add a file to our ``list.yaml``\.

::

    body: goodies/list/list.html
    title: Goodies

    js:
        - url: {{ MEDIA_URL }}js/jquery.js
        - static: goodies/list/media/js/animate.js

Now we put ``animate.js`` in ``templates/goodies/list/media/js/animate.js``\, and edit this file ::

    $(document).ready(function() {
        $('p').hide().show();
    })

Why are we putting this in ``templates/goodies/list/media/js/``\.  Django's convention
states that this should really go somewhere in the ``MEDIA_ROOT``\.  The
decision we made with CrunchyFrog is that your views typically involve a group
of files and directories to make a specific thing happen.  We'd rather see
everything stick together in one place as opposed to stringing the files out in
different directories.

So now our files for this page assembly look like this::

    ./templates/goodies/list/list.yaml
    ./templates/goodies/list/list.html
    ./templates/goodies/list/media/js/animate.js

Now before you object to static files being served outside of the
``MEDIA_ROOT`` let's look at the source code that CrunchyFrog produces. ::

    <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
    <html lang="en">
        <head>
            <title>Goodies</title>
            <script type="text/javascript" src="http://localhost:8000/site_media/js/jquery.js"></script>
            <script type="text/javascript" src="http://localhost:8000/site_media/cfcache/goodies/list/media/js/animate.js"></script>
        </head>

        <body>
            <h1>Whizzo Chocolates</h1>

            <p>My favorite is Ram&#39;s bladder cup</p>
        </body>
    </html>

Note that even though we had ``animate.js`` inside our templates directory, it's
now being served out of the ``site_media`` static files locations.  CrunchyFrog
copied this file into the cache for you.

Time for some CSS.  Let's create a new file in ``templates/goodies/list/media/css/screen.css``\.

::

    body {
        background-color: lightblue;
        font-family: sans-serif;
    }

    p {
        padding: 3em;
        background-color: lightyellow;
    }

Add this to our YAML file::

    body: goodies/list/list.html
    title: Goodies

    js:
        - url: {{ MEDIA_URL }}js/jquery.js
        - static: goodies/list/media/js/animate.js

    css:
        - static: goodies/list/media/css/screen.css

The resulting HTML looks like this::

    <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
    <html lang="en">
        <head>
            <title>Goodies</title>
            <link rel="stylesheet" type="text/css" href="http://localhost:8000/site_media/cfcache/goodies/list/media/css/screen.css" media="screen"/>
            <script type="text/javascript" src="http://localhost:8000/site_media/js/jquery.js"></script>
            <script type="text/javascript" src="http://localhost:8000/site_media/cfcache/goodies/list/media/js/animate.js"></script>
        </head>

        <body>
            <h1>Whizzo Chocolates</h1>

            <p>My favorite is Ram&#39;s bladder cup</p>
        </body>
    </html>

Changing the DOCTYPE declaration
--------------------------------

If you'd like to change the doctype, you can do that in the YAML file.  Be
default it's going to be HTML 4.01 Transitional.

Here's how you change it ::

    doctype: XHTML 1.0 Strict
    body: goodies/list/list.html
    title: Goodies

    js:
        - url: {{ MEDIA_URL }}js/jquery.js
        - static: goodies/list/media/js/animate.js

    css:
        - static: goodies/list/media/css/screen.css

The resulting HTML looks like this::

    <!DOCTYPE HTML PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/xhtml1-strict.dtd">
    <html lang="en">
        <head>
            <title>Goodies</title>
            <link rel="stylesheet" type="text/css" href="http://localhost:8000/site_media/cfcache/goodies/list/media/css/screen.css" media="screen" />
            <script type="text/javascript" src="http://localhost:8000/site_media/js/jquery.js"></script>
            <script type="text/javascript" src="http://localhost:8000/site_media/cfcache/goodies/list/media/js/animate.js"></script>
        </head>

        <body>
            <h1>Whizzo Chocolates</h1>

            <p>My favorite is Ram&#39;s bladder cup</p>
        </body>
    </html>

Adding some assets for template tags
------------------------------------

What happens if you have a yaml file for assests when you have template tag and want to use
the CrunchyFrog framework? Luckly we have thought about that and have made it really, really
easy. All you have to do is use a simple python decorator in your template tag class and
you are ready to roll.

Here is a sample template tag class::

    from django import template

    register = template.Library()z

    @register.tag(name="testtag")
    def do_test(parser, token)
        return TestNode()

    class TestNode(template.Node):
        def render(self, context):
            # Here you can render a template or return some type of HTML string
            return 'Some HTML stuff'

To add assests from a yaml file to the page using CrunchyFrog::

    from django import template
    from crunchyfrog.renderer import add_yaml # Add this import

    register = template.Library()z

    @register.tag(name="testtag")
    def do_test(parser, token)
        return TestNode()

    class TestNode(template.Node):
        @add_yaml('template/path/to/yaml/file/test.yaml')
        def render(self, context):
            # Here you can render a template or return some type of HTML string
            return 'Some HTML stuff'

That is all that it takes to have CSS, META, JS , etc. assests included in the page header
using the CrunchyFrog framework for a template tag and any templates it renders.

.. _Flex: http://www.adobe.com/products/flex/
.. _Sproutcore: http://www.sproutcore.com/
.. _Cappuccino: http://cappuccino.org/
