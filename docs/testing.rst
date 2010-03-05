==========================================
Testing Javascript with a browser and Ribt
==========================================

.. todo: Intro about writing tests with Selenium and Windmill, what's wrong with
   it and how Dojo's DOH changes the premise

Instrumenting your site
-----------------------

CrunchyFrog does not include the files it needs to run tests in normal everyday
development or production.  We have to instruct it that we are testing.  To do
that we'll change a setting.

In your :file:`settings.py` file, add this ::

    CRUNCHYFROG_RIBT_INSTRUMENTED = True

Telling CrunchyFrog about your tests
------------------------------------

Edit the YAML file, adding a ``tests`` instruction ::

    ...

    ribt:
        - namespace: Whizzo.Goodies.List
          location: goodies/list/media/js
          require:
            - Whizzo.Goodies.List.Controller
            - Whizzo.Goodies.List.View
          tests:
            - Whizzo.Goodies.List.Test

This works like the Controller and the View.  It looks for a file called
:file:`Test.js` within the :file:`goodies/list/media/js` directory.

If you've gone through the tutorial, you've already created Dojo-based classes
like this.

Now, create :file:`goodies/list/media/js/Test.js`, starting it out like this ::

    dojo.provide('Whizzo.Goodies.List.Test');

    dojo.require('RibtTools.TestRunner.TestCase');

    dojo.declare('Whizzo.Goodies.List.Test', RibtTools.TestRunner.TestCase, {
        testCanSeeJQueryTabs: function() {
            this.exists('div.ui-tabs');

            this.then(function() {
                var view = this.getController('Whizzo.Goodies.List.View')[0];

                view.numberFrogsEaten.value = '5';

                view.tellUsAboutFrogsOnClick(undefined);
            });
        }
    });
    
Run your test
-------------

Now that we've created the test, and we will get into the meaning of each line
later, let's run it.

Make sure that your server is running ::

    ./manage.py runserver

In your browser go to http://127.0.0.1:8000/goodies/list.  Remember that this is
based on our demo application, so we've defined this URL in the normal Django-ish
way in the :file:`urls.py` module.


