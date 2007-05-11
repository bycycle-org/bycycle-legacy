#!python
from setuptools import setup, find_packages

setup (
    name='bycycle.tripplanner',
    version='0.5a0',
    author='Wyatt Baldwin, byCycle.org',
    author_email='wyatt@bycycle.org',
    description='Zope3 version of the byCycle.org Trip Planner',
    license='None yet',
    keywords='zope3',
    url='',
    packages=find_packages('src'),
    include_package_data = True,
    package_dir={'': 'src'},
    namespace_packages = ['bycycle'],
)
