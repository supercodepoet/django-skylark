===============
Using CleverCSS
===============
`CleverCSS`_ is a small markup language for CSS inspired by Python.  We like it
so much that we integrated it directly into CrunchyFrog.

.. note:: We are going to use the project we set up in :doc:`getting started</gettingstarted>` and
          things will work out much better if you do too

Let's start with creating a new css file called
``goodies/templates/goodies/list/media/css/clever.css`` ::

    main_background_color = chocolate

    html:
        background->
            color: $main_background_color

This is what a CleverCSS file looks like.  This particular one is very simple,
but uses constants and the Python-like syntax that made us want to buy
CleverCSS flowers and take it to a nice dinner.

We won't spend a lot of time going into the bits of CleverCSS because you
should really `check it out for yourself`__.

__ CleverCSS_

Now it's time to edit our YAML file to include this.  So edit
``goodies/templates/goodies/list/list.yaml`` ::

    title: Some title here for goodies
    body: goodies/list/list.html

    css:
        - static: goodies/list/media/css/screen.css
          media: screen

        - static: goodies/list/media/css/clever.css
          process: clevercss
          media: screen

CrunchyFrog will grab the file and automatically run it through the CleverCSS
interpreter and include the results on your page assembly.

So make sure your server is running now ::

    python manage.py runserver

Once it's up, go to ``http://127.0.0.1:8000``

You should see a nice chocolate background on your page.  Let's take a quick
peek at the output from the CSS file.

Here is the page's output ::

    <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
    <html lang="en">
    <head>

        <title>Some title here for goodies</title>

        <link rel="stylesheet" type="text/css" href="http://127.0.0.1:8000/sitemedia/cfcache/goodies/list/media/css/screen.css" media="screen" />

        <link rel="stylesheet" type="text/css" href="http://127.0.0.1:8000/sitemedia/cfcache/goodies/list/media/css/clever.css" media="screen" />

        <script type="text/javascript">
            //<![CDATA[
            // Injected by Django CrunchyFrog
            var $CF = { MEDIA_URL: "http://127.0.0.1:8000/sitemedia/cfcache/" }
            //]]>
        </script>

    </head>

    <body>
        <h1>Your page is working (using only the finest baby frogs, dew picked and flown in from Iraq)</h1>
    </body>

    </html>


And the source of ``http://127.0.0.1:8000/sitemedia/cfcache/goodies/list/media/css/clever.css`` ::

    html {
        background-color: chocolate;
    }


.. _CleverCSS: http://sandbox.pocoo.org/clevercss/
