==================================
Django Skylark Javascript bridging
==================================

Django Skylark output a special Javascript section in your page that gives you
access to certain information.  If you view source on a Django Skylark generated
page you can see the following block. ::

    <script type="text/javascript">
        //<![CDATA[
        // Injected by Django Skylark
        var $CF = { MEDIA_URL: "http://127.0.0.1:8000/sitemedia/cfcache/" }
        //]]>
    </script>

From within Javascript that you write, you can rely on this variable to give
you access to any of the content that Django Skylark is caching.

Later on we'll add more information to this special ``$CF`` variable.  For now, it's kinda light.
