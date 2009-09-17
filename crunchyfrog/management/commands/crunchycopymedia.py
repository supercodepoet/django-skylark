#!/usr/bin/env python

from django.core.management.base import BaseCommand, CommandError
from django.template import loader
from optparse import make_option
from crunchyfrog.renderer import Renderer
from crunchyfrog.conf import settings

import hashlib
import os

class Command(BaseCommand):
	help = "This command will copy a media file to the CrunchyFrog media cache."

	option_list = BaseCommand.option_list + (
		make_option("-f", "--file", dest="file", default=None, type="string",
					help="The file to copy in the media cache, example: /blog/base.js."),
		make_option("-p", "--process", dest="process", default=None, type="string",
					help="The name of the process func that should be used, example: clevercss."),
	)

	def handle(self, file=None, process=None, *args, **kwargs):
		if not file:
			raise CommandError("You must specifiy the file to copy.")

        # Might be able to use renderer.copy_to_media to enable this
        #renderer = Renderer()

		basename, extension = os.path.splitext(file)
		filename = hashlib.md5(file).hexdigest() + extension
		fullpath = os.path.join(settings.CRUNCHYFROG_CACHE_ROOT, filename)

		source, origin = loader.find_template_source(file)

		if process:
			process_func = Renderer.processing_funcs[process]
			source = process_func(source)

		f = open(fullpath, 'w')
		f.write(source)
		f.close()
