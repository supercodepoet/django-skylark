========================
Rendering pieces of HTML
========================

Page assemblies are fine, but there are occasions when you just need to render a
chunk of HTML and you don't want the HTML and HEAD sections but you still want
the ``<script>`` and ``<link>`` tags that CrunchyFrog will produce when you
render an assembly.

This is possible with ``SnippetAssembly``.

Snippet assemblies
------------------

Here's an example of a SnippetAssembly::

    from django.http import HttpResponse
    from crunchyfrog.snippet import SnippetAssembly, RequestContext

    def list(request):
        c = RequestContext(request, {
            'confection': "Ram's bladder cup"
        })

        sa = SnippetAssembly('goodies/ajax.yaml', c)

        return sa.get_http_response()

Everything is exactly the same, except you use a ``SnippetAssembly`` instead of
a ``PageAssembly``.

Here is what you get ::

        <link rel="stylesheet" type="text/css" href="http://localhost:8000/site_media/cfcache/goodies/list/media/css/screen.css" media="screen" />
        <script type="text/javascript" src="http://localhost:8000/site_media/js/jquery.js"></script>
        <script type="text/javascript" src="http://localhost:8000/site_media/cfcache/goodies/list/media/js/animate.js"></script>
        <h1>You bet it&apos;s AJAX!</h1>
