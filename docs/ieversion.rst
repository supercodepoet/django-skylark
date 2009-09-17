===========================
IE Conditional CSS comments
===========================

Internet Explorer is not very popular in developer's eyes.  There is quite a
lot of material written on how to deal with it's shortcomings.

A popular technique to deal with it's CSS differences is to use conditional
comments.  They look like this. ::

    <!--[if IE 6]>
    Special instructions for IE 6 here
    <![endif]-->

These have to appear in the HTML.  Typically, you would put a ``<link>`` tag in
there that points to a css file with just those special styles.

We can do this in CrunchyFrog by using the ``ieversion`` attribute. ::

    body: goodies/list/list.html
    title: Goodies

    js:
        - url: {{ MEDIA_URL }}js/jquery.js
        - static: goodies/list/media/js/animate.js

    css:
        - static: goodies/list/media/css/screen.css
        - static: goodies/list/media/css/ie6.css
          ieversion: IE 6

Possible values
---------------

Withing your ``css`` section of your YAML file you put the following ::

    css:
        - static: goodies/list/media/css/ie6.css
          ieversion: [CONDITION]

So put something like this in for ``CONDITION`` :

``IE 6``
    Only Internet Explorer 6

``gte IE 6``
    If it's greater than or equal to Internet Explorer 6

``lt IE 7``
    If it's less than Internet Explorer 7

.. note:: You don't need the ``if`` in front of the condition.  CrunchyFrog will do this for you.  Just put the condition there.

What does it produce
--------------------

If you look at the output once CrunchyFrog outputs your page you'll see some
HTML comments around the ``<link>`` tag referencing your CSS file.  This
comment is special in the eyes of Internet Explorer.  It will look for this
formatting and evaluate the condition you have inside.

If you did this ::
    
    css:
        - static: goodies/list/media/css/ie6.css
          ieversion: lt IE 8

You get this in you page ::

    <!--[ if lt IE 8 ]>
    <link rel="stylesheet" type="text/css" href="/media/cfcache/goodies/list/media/css/ie6.css" media="all">
    <![endif]-->
