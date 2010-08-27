from skylark import plans
from django.conf import settings

if settings.DEBUG:
    default = plans.ReusableFiles
    plans.plan_options(minify_javascript=False)
else:
    default = plans.ReusableFiles
