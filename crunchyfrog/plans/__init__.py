from django.utils.functional import memoize

from base import BasePlan
from fewest import FewestFiles
from reusable import ReusableFiles
from separate import SeparateEverything

__all__ = ['MissingMediaPlan', 'get_plan', 'plan_options', 'get_for_context']
__plan_cache = {}


def get_plan(module, attr):
    plans = __import__(module, globals(), locals(), attr)

    return getattr(plans, attr)
get_plan = memoize(get_plan, __plan_cache, 2)


def plan_options(**kwargs):
    BasePlan.set_options(**kwargs)


class MissingMediaPlan(Exception):
    pass


def get_for_context(context, render_full_page):
    try:
        from crunchyfrog.conf import settings
        plan = get_plan(
            settings.CRUNCHYFROG_PLANS,
            settings.CRUNCHYFROG_PLANS_DEFAULT)

        from base import BasePlan
        if isinstance(plan, BasePlan):
            """
            We actually want the class here, not an instance of it
            """
            raise ValueError('Do not set the plan to an instance of %s, pass '
                 'us the actual class object itself' % plan)

        if not render_full_page:
            # Only supported plan for snippets is separating everything
            return SeparateEverything(context, render_full_page)
        else:
            return plan(context, render_full_page)
    except ImportError:
        if settings.DEBUG:
            return SeparateEverything(context, render_full_page)
        else:
            raise MissingMediaPlan('Could not import the media plan for '
                'CrunchyFrog media deployment: %s name %s' % (
                    settings.CRUNCHYFROG_PLANS,
                    settings.CRUNCHYFROG_PLANS_DEFAULT,
                ))
