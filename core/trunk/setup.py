###############################################################################
# $Id$
# Created 2006-09-07
#
# Project setup for byCycle Core.
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
    name='byCycleCore',
    version='0.4a0',
    description='byCycle Core Services -- PostgreSQL/PostGIS/SQLAlchemy version',
    long_description="""\
Address normalization, geocoding, routing and other GIS-related services. We
still have not decided on a license, but it will most likely end up being the
GPL.""",
    license='Free For Home Use',
    author='Wyatt L Baldwin, byCycle.org',
    author_email='wyatt@byCycle.org',
    keywords='bicycle bike cycyle trip planner route finder',
    url='http://bycycle.org/',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
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
        'zope.interface==3.3.0.1',
        'PCL-Core==0.11.0',
        'psycopg2==2.0.7',
        'SQLAlchemy==0.3.7',
        'Dijkstar>=1.0',
        'nose>=0.10.3',
        'simplejson>=1.9.2',
        ),
)

