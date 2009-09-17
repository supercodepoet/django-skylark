#!/usr/bin/env python

from django.core.management.base import BaseCommand, CommandError
from django.core.cache import cache
from optparse import make_option

import hashlib

class Command(BaseCommand):
	help = "This command will clear the configured cache of the PageInstruction object given the correct Django view."

	option_list = BaseCommand.option_list + (
		make_option("", "--host", dest="host", default=None, type="string",
                    help="The host on which the view function exists.  Example: 127.0.0.1:8000"),
		make_option("", "--view", dest="view", default=None, type="string",
                    help="The view function of the PageInstruction to clear from the cache.  Example: list"),
		make_option("-k", "--key", dest="key", default=None, type="string",
					help="The cache key used to find the PageInstruction object."),
	)

	def handle(self, host=None, view=None, key=None, *args, **kwargs):
		if not host:
			raise CommandError("A host is needed to know where the view exits.")

		if not view and not key:
			raise CommandError("A view or key must defined to remove the object from cache.")

		md5 = hashlib.md5()
		md5.update(host)

		if key:
			md5.update(key)
		else:
			md5.update(view)

		cache_key = "crunchy_frog::page_instructions::%s" % (md5.hexdigest(),)
		cache.delete(cache_key)

		print self.style.NOTICE("If the PageInstruction was cached, it was deleted from the cache.")
