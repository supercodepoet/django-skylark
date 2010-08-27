=====================
YAML option reference
=====================

TODO YAML files are templates.

``body``
--------

Let's you specifiy a template to use when rendering the page.  Remember you
shouldn't be including the HTML or HEAD sections, Django Skylark will do this for
you.

Here is an example template

**goodies/list/list.html** ::

    <body>
        <h1>I love chocolate</h1>
    </body>

**goodies/list/list.yaml** ::

    body: goodies/list/list.html

``title``
---------

The title of the document.  This will go inside of the ``<title>`` HTML tag.

**goodies/list/list.yaml** ::

    title: This is my list of Whizzo stuff

``uses``
--------

``js``
------

``static``
~~~~~~~~~~

``inline``
~~~~~~~~~~

``url``
~~~~~~~

``css``
-------

``static``
~~~~~~~~~~

``inline``
~~~~~~~~~~

``url``
~~~~~~~

``media``
~~~~~~~~~

``process: clevercss``
~~~~~~~~~~~~~~~~~~~~~~
