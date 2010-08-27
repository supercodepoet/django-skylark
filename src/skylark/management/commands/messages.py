MESSAGE_HELP = \
"""This command will create a Django Skylark page and kick start a configuration
file for you

Do something like this:
    ./manage.py skylarkpage -a goodiesapp -p list

Will create a page called "list" in the goodiesapp"""

MESSAGE_CONFIRM_TEMPLATE_CREATION = \
"""We've found your app but no templates directory.

We can create this for you and continue from here if you like.

Create %s (yes/no)? """

MESSAGE_CONFIRM_CREATION = """We're about to create these directories:

%s

And these files

%s

Are you sure you want to do this (yes/no)? """

CONTENT_YAML = \
"""title: Some title here for %(app)s
body: %(page_directory)s/%(page)s.html

#js:
    # Here are some examples (delete these if you don't use them)
    #- url: http://somewhere.com/js/javascript.js
    #- static: app/page/js/path.js

css:
    - static: %(page_directory)s/media/css/screen.css
      media: screen

    # Here are some examples (delete these if you don't use them)

    #- url: {{ MEDIA_URL }}/css/handheld.css
    #  media: all

    #- render: app/page/css/dynamic.css
    #  media: handheld, print, screen

    #- static: app/page/css/clevercss.css
    #  process: clevercss
    #  media: screen
"""

CONTENT_HTML = """<body>
    <h1>Your page is working (using only the finest baby frogs, dew picked and
    flown in from Iraq)</h1>
</body>"""

CONTENT_VIEW = """from django.http import HttpResponse
from skylark.page import PageAssembly, RequestContext

def %(page)s(request):
    c = RequestContext(request, {
        #'name': "value"
    })

    pa = PageAssembly('%(page_directory)s/%(page)s.yaml', c)

    return pa.get_http_response()
"""
