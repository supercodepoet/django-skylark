import planapp
from crunchyfrog import plans
from django.conf import settings

if settings.DEBUG:
    default = plans.SeparateEverything
else:
    #default = plans.FewestFiles
    default = plans.ReusableFiles

"""
Eventually we want to be able to apply settings for specific views, this seemed
like a good idea when we were designing this feature but it may turn out to be
bunk.
"""
#plans.apply_to(planapp.views.index, plans.FewestFiles)
#default.apply_to(views.full.someview, plans.SeparateEverything)
