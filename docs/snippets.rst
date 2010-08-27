========================
Rendering pieces of HTML
========================

Page assemblies are fine, but there are occasions when you just need to render a
chunk of HTML and you don't want the HTML and HEAD sections but you still want
the ``<script>`` and ``<link>`` tags that Django Skylark will produce when you
render an assembly.

This is possible with ``SnippetAssembly``.

.. todo:: This really needs some updating, the section "Here is what you get" is
   completely wrong at this point.  And we need to update the usage.  Once for
   AJAX and one for template tags.  This is confusing we've found out at LB.

Snippet assemblies
------------------

Here's an example of a SnippetAssembly::

    from django.http import HttpResponse
    from skylark.snippet import SnippetAssembly, RequestContext

    def list(request):
        c = RequestContext(request, {
            'confection': "Ram's bladder cup"
        })

        sa = SnippetAssembly('goodies/ajax.yaml', c)

        return sa.get_http_response()

If you are using a SnippetAssembly in a template tag, you can also call
:meth:`dumps` ::

    def render(self, context):
        sa = SnippetAssembly('goodies/ajax.yaml', context)

        return sa.dumps()

Everything is exactly the same, except you use a ``SnippetAssembly`` instead of
a ``PageAssembly``.

Here is what you get ::

        <h1>You bet it&apos;s AJAX!</h1>
