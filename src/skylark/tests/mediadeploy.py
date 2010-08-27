import planapp
from skylark import plans
from django.conf import settings

se = plans.SeparateEverything
rf = plans.ReusableFiles
ff = plans.FewestFiles

if settings.DEBUG:
    default = se
else:
    #default = plans.FewestFiles
    default = rf

"""
Eventually we want to be able to apply settings for specific views, this seemed
like a good idea when we were designing this feature but it may turn out to be
bunk.
"""
#plans.apply_to(planapp.views.index, plans.FewestFiles)
#default.apply_to(views.full.someview, plans.SeparateEverything)
