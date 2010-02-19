from crunchyfrog import plans
from django.conf import settings

if settings.DEBUG:
    default = plans.ReusableFiles
    #default = plans.SeparateEverything
else:
    default = plans.ReusableFiles
