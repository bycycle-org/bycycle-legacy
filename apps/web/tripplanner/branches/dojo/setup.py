###############################################################################
# $Id: setup.py 459 2007-02-15 12:05:14Z bycycle $
# Created 2006-09-07
#
# Project setup for byCycle Trip Planner.
#
# Copyright (C) 2006, 2007 Wyatt Baldwin, byCycle.org <wyatt@bycycle.org>.
# All rights reserved.
#
# For terms of use and warranty details, please see the LICENSE file included
# in the top level of this distribution. This software is provided AS IS with
# NO WARRANTY OF ANY KIND.
###############################################################################
from setuptools import setup, find_packages

setup(
    name='byCycleTripPlanner',
    version='0.4a0',
    
    description='byCycle Trip Planner -- Pylons version',
    long_description='byCycle Trip Planner Web Application',

    license='Free For Home Use',
    
    author='Wyatt L Baldwin, byCycle.org',
    author_email='wyatt@byCycle.org',

    keywords='bicycle bike cycyle trip planner route finder',
    
    url='http://bycycle.org/',
    download_url='http://guest:guest@svn.bycycle.org/apps/web/tripplanner/branches/dojo#egg=byCycleTripPlanner-dev',

    classifiers=[
    'Development Status :: 3 - Alpha',
    'Environment :: Web Environment',
    'Framework :: Paste',
    'Intended Audience :: Developers',
    'License :: Free For Home Use',
    'Natural Language :: English',
    'Programming Language :: Python',
    'Topic :: Other/Nonlisted Topic',
    'Topic :: Scientific/Engineering :: GIS',
    ],
    
    packages=find_packages(),
    
    zip_safe=False,
    
    install_requires=(
    'byCycleCore==0.4a0.dev',
    'Pylons>=0.9.4.1',
    ),

    test_suite = 'nose.collector',

    package_data={'tripplanner': ['i18n/*/LC_MESSAGES/*.mo']},

    entry_points="""
    [paste.app_factory]
    main=tripplanner:make_app
    [paste.app_install]
    main=paste.script.appinstall:Installer
    """,
    )
