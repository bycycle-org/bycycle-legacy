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

    description='byCycle Core Services',
    long_description='Address normalization, geocoding, routing and other GIS-related services',
    
    license='Restricted personal use only',
    
    author='Wyatt L Baldwin',
    author_email='wyatt@byCycle.org',
    
    url='http://bycycle.org/',
    download_url='http://svn.bycycle.org/core/branches/enterprise#egg=byCycleCore-dev',
    
    classifiers=[
    'Development Status - Alpha',
    'License :: Restricted personal use only',
    'Intended Audience :: Developers',
    'Programming Language :: Python',
    'Environment :: Console',
    ],

    packages=find_packages(),

    zip_safe=False,

    install_requires=(
    'psycopg2==2.0.6b1',
    'SQLAlchemy==0.3.4',
    'zope.interface==3.3.0',
    ),
)
