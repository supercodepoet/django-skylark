from django.core.management.base import BaseCommand, CommandError
from django.core.cache import cache
from django.utils.importlib import import_module
from optparse import make_option
from messages import *
from skylark.conf import settings

import os
import hashlib


class Command(BaseCommand):
    help = MESSAGE_HELP

    option_list = BaseCommand.option_list + (
        make_option("--noconfirm", "-n", dest="noconfirm", action="store_true",
            help="Whether we show you a summary of what will happen and let "
                "you confirm"),
        make_option("--app", "-a", dest="app",
            help="The application to add a page to"),
        make_option("--page", "-p", dest="page",
            help="The page name you wish to create inside the app"),
    )

    def handle(self, *args, **options):
        if len(args) > 0:
            # Display the help and quit this foolishness
            self.print_help('skylarkpage', '')
            return

        # Here is our args
        app = options.get('app')
        page = options.get('page')
        noconfirm = True if options.get('noconfirm') == True else False
        self.confirm = not noconfirm

        if not app:
            raise CommandError("You must provide the app name, here's what "
               "you have in settings: %s" % settings.INSTALLED_APPS)

        if not page:
            raise CommandError("You must provide the page name")

        # We look for the application in the directory, and for a templates
        # directory
        try:
            appobject = import_module(app)
            directory = os.path.dirname(appobject.__file__)
        except ImportError:
            raise CommandError("The app %s could not be imported.  Is it on "
               "your python path?" % app)

        tmp_dir = os.path.join(directory, 'templates')

        if not os.path.isdir(tmp_dir) and self.confirm:
            create_tmp_dir = raw_input(self.style.NOTICE(
                MESSAGE_CONFIRM_TEMPLATE_CREATION % tmp_dir))
            if create_tmp_dir == 'yes':
                os.mkdir(tmp_dir)

        if not os.path.isdir(tmp_dir):
            raise CommandError("The templates directory is missing")

        page_dir = os.path.join(app.replace(".", os.sep), page)

        dirs_to_create = (
            os.path.join(tmp_dir, page_dir, 'media'),
            os.path.join(tmp_dir, page_dir, 'media', 'css'),
            os.path.join(tmp_dir, page_dir, 'media', 'img'),
            os.path.join(tmp_dir, page_dir, 'media', 'js'),
            os.path.join(tmp_dir, page_dir, 'media', 'js', 'templates'),
        )

        files_to_create = (
            os.path.join(tmp_dir, page_dir, 'media', 'css', "screen.css"),
            os.path.join(tmp_dir, page_dir, 'media', 'js', "%s.js" % page),
        )

        if self.confirm:
            ok_to_create = self.__confirm_creation(
                dirs_to_create, files_to_create)

            if ok_to_create:
                self.__create_these(dirs_to_create, files_to_create)
            else:
                raise CommandError("Ok, fine, we won't touch it if you've "
                   "changed your mind")
        else:
            self.__create_these(dirs_to_create, files_to_create)

        """
        Now we're gonna make the YAML and HTML files
        """
        context = {'app': app, 'page': page, 'page_dir': page_dir}
        yaml_file = os.path.join(tmp_dir, page_dir, "%s.yaml" % page)
        html_file = os.path.join(tmp_dir, page_dir, "%s.html" % page)

        self.__fill_file(yaml_file, CONTENT_YAML, context)
        self.__fill_file(html_file, CONTENT_HTML, context)

        print self.style.NOTICE(
            "\nYou can do something like this in your view now\n")

        print CONTENT_VIEW % {'app': app, 'page': page, 'page_dir': page_dir}

    def __fill_file(self, file, content_format, context={}):
        """
        Acts as a poor mans template engine, replacing the tokens in
        content_format with stuff in context and then writes it to
        file if it doesn't exist
        """
        if os.path.isfile(file):
            print self.style.ERROR(
                "%s already exists, we won't mess with it" % file)
        else:
            print self.style.NOTICE("\nWriting file:\n%s" % file)

            f = open(file, 'w')
            f.write(content_format % context)
            f.close()

    def __confirm_creation(self, dirs_to_create, files_to_create):
        """
        Make sure that the user wants to do this
        """
        cwd = os.getcwd()
        shorthand = "."

        answer = raw_input(self.style.NOTICE(
            MESSAGE_CONFIRM_CREATION % (
                "\n".join(dirs_to_create).replace(cwd, shorthand),
                "\n".join(files_to_create).replace(cwd, shorthand),
            )))

        if answer.lower.startswith('y'):
            return True

        return False

    def __create_these(self, dirs_to_create, files_to_create):
        """
        Makes the directories and files needed by Django Skylark
        """
        already_exists_message = "%s already exists, skiping"

        for dir in dirs_to_create:
            if os.path.isdir(dir):
                print self.style.ERROR(already_exists_message % dir)
                continue

            os.makedirs(dir)

        for file in files_to_create:
            if os.path.isfile(file):
                print self.style.ERROR(already_exists_message % file)
                continue

            open(file, 'a').close()
