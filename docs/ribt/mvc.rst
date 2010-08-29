=======================
Ribt MVC implementation
=======================

What's it for?
--------------

The MVC implementation is for developers writing applications in Javscript in the
browser.  

This can include the use of JQuery, Dojo, MooTools, Prototype, Scriptaculous or
any other framework for developing Javascript.  By using Ribt, we don't force
you to do things "our" way.

The goal?
---------

In Javascript development, there are many libraries that provide an abstraction
on top of the nativ DOM that make developing Javascript easier.  Ribt uses Dojo
as its low-level library.

There are also libraries like ExtJS, JQuery UI, and Dijt that provide pre-packaged UI
implementations.  These allow you to define layouts, make sortable lists, tabbed
interfaces, etc.

Ribt sits between a low-level library and a user interface patterns implementation.

Our goal is to make Javascript development easier by extracting common patterns
and providing tools to develop with.

What tools do we provide?
-------------------------

We'll get into the details of what these are, at first it's not apparent.  But
this is a laundry list of the things we are trygin to solve with Ribt.

* An MVC pattern implementation in Javascript
* Integration with Django Skylark
* Automatic bootstrapping of objects
* Data binding for passing in simple information to your objects
* Event binding, for example tying the onclick event to a method in you object
* Javascript templating using Dojo's DTL (Django Template Language) library

Here are some of the projects that gave us ideas as we worked on this:

* http://javascriptmvc.com/ We like the general idea, but felt the separation of
  the Model into it's own concern wasn't necessary.  Our data interaction
  happens within our controller.
* http://cappuccino.org/ Great framework but it focused on creating Desktop
  application for the web.  This was not our direction.
* http://sproutcore.com/ Used by Apple for MobileMe and is one we stole a lot of
  ideas from. 

We use Dojo, but that doesn't mean you can't use X
--------------------------------------------------

We made the choice to use Dojo as the backend of our implementation.  This does
not mean you can't use JQuery.  In fact, it was a requirement that we didn't
*develop out* the possibility to use other libraries.

You'll also notice as you go through our documentation that many of our examples
use JQuery to do some basic things.

Handling the dependency on Dojo
-------------------------------

.. todo:: Describe the SKYLARK_DOJO_VIA settings
