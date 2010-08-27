from django.conf import settings


def media(request):
    from skylark.plans import get_plan
    plan = get_plan(settings.SKYLARK_PLANS,
                    settings.SKYLARK_PLANS_DEFAULT)
    return {
        'MEDIA_URL': settings.MEDIA_URL,
        'CF_MEDIA_URL': '%s%s/' % (
            settings.SKYLARK_CACHE_URL, plan.cache_prefix,)}
