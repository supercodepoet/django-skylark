from django.http import HttpResponse

def index(request):
    return HttpResponse('')

def badview(request):
    import somethingnothere
