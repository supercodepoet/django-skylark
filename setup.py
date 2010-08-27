from setuptools import setup, find_packages
import os

from pkginfo import version

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
NEWS = open(os.path.join(here, 'NEWS.rst')).read()

install_requires = [
    # http://packages.python.org/distribute/setuptools.html#declaring-dependencies
    'pyyaml==3.09',
    'pytidylib==0.2.1',
]

setup(
    name='django-skylark',
    version=version,
    description="",
    long_description=README + '\n\n' + NEWS,
    classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='web 2 html css mvc django dojo yaml',
    author='Rob Madole',
    author_email='robmadole@gmail.com',
    url='http://robmadole.com',
    license='BSD',
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
      'pyyaml==3.09',
      'pytidylib==0.2.1',
    ],
    entry_points={}
)
