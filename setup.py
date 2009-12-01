from setuptools import setup, find_packages
import sys, os

from pkginfo import version

setup(name='django-crunchyfrog',
      version=version,
      description="Web 2.0 developement, lightly killed, and covered in chocolate",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='web 2 html css mvc django dojo clevercss yaml',
      author='Rob Madole',
      author_email='robmadole@gmail.com',
      url='http://robmadole.com',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'pyyaml',
          'pytidylib',
          'cssutils',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
