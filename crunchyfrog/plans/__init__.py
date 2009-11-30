from fewest import FewestFiles
from reusable import ReusableFiles
from separate import SeparateEverything

def get_for_context(context, render_full_page):
    try:
        from crunchyfrog.conf import settings
        plans = __import__(settings.CRUNCHYFROG_PLANS)

        plan = getattr(plans, settings.CRUNCHYFROG_PLANS_DEFAULT)

        from base import BasePlan
        if isinstance(plan, BasePlan):
            """
            We actually want the class here, not an instance of it
            """
            raise ValueError('Do not set the plan to an instance of %s, pass '
                 'us the actual class object itself' % plan)

        return plan(context, render_full_page)
    except ImportError:
        return SeparateEverything(context, render_full_page)
