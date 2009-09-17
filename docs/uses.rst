=====================================
Extending (or using) other YAML files
=====================================
It's important to adhere to the DRY principal. In case you have forgotten this
stands for "Do not Repeat Yourself".  Django Templates allow you to extend one
template with another.  CrunchyFrog allows you to specify another YAML file
within your own.

Here's how this works.  Let's create a YAML file with everything we need called ``add.yaml`` ::

    body: goodies/add/add.html
    title: Add a new goody

    js:
        - url: {{ MEDIA_URL }}js/jquery.js
        - url: {{ MEDIA_URL }}js/dojo.js
        - static: common/media/js/logging.js

    css:
        - static: common/media/css/reset.css
        - static: common/media/css/fonts.css
        - static: goodies/add/media/css/screen.css

Looks good.  But we realize that as soon as we make an Edit and Delete page we
are going to be including some common stuff.  It would be nice not to list the
jQuery, CSS reset and fonts, and logging javascript every time.

So, let's use the ``uses`` attribute to refactor this:

We'll start by making a ``common.yaml`` ::

    js:
        - url: {{ MEDIA_URL }}js/jquery.js
        - url: {{ MEDIA_URL }}js/dojo.js
        - static: common/media/js/logging.js

    css:
        - static: common/media/css/reset.css
        - static: common/media/css/fonts.css
    
The idea here is that it's a common file.  We use jQuery, Dojo, and a
javascript library we wrote for general logging.  (Just pretend ok).

Now our ``add.yaml`` becomes this ::

    body: goodies/add/add.html
    title: Add a new goody

    uses:
        - file: common/common.yaml

    css:
        - static: goodies/add/media/css/screen.css

Behind the scenes CrunchyFrog will run across this instruction and add the
common.yaml file to its list of page instructions.

.. note:: The order is important when you are dealing with Javascript and CSS.
          If you "use" another YAML file, it will be included first before any of your
          other dependencies

Our directory structure would look something like this ::

    ./common/common.yaml
    ./common/media/js/logging.js
    ./common/media/css/reset.css
    ./common/media/css/fonts.css
    ./goodies/add/add.yaml
    ./goodies/add/add.html
    ./goodies/add/media/css/screen.css
