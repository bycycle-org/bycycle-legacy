###########################################################################
# $Id$
# Created 2006-09-07
#
# Distutils setup.
#
# Copyright (C) 2006 Wyatt Baldwin, byCycle.org <wyatt@bycycle.org>.
# All rights reserved.
#
# For terms of use and warranty details, please see the LICENSE file included
# in the top level of this distribution. This software is provided AS IS with
# NO WARRANTY OF ANY KIND.


from distutils.core import setup


setup(
    name='byCycle',
    description='byCycle Trip Planner',
    long_description='byCycle Trip Planner',
    author='Wyatt L Baldwin',
    author_email='wyatt@byCycle.org',
    url='http://www.byCycle.org/',
    version='0.3.5a',
    classifiers=[
        'Development Status - Alpha',
        'License :: Restricted personal use only',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Environment :: Console',
        'Environment :: Web Environment',
        ],
    packages=[
        'lib',
        'model',
        'model.data',
        'model.tests',
        'model.milwaukeewi',
        'model.milwaukeewi.data',
        'model.portlandor',
        'model.portlandor.data',
        'model.pittsburghpa',
        'model.pittsburghpa.data',
        'scripts',
        'services',
        'services.normaddr',                
        'services.geocode',                
        'services.route',
        ],
)
