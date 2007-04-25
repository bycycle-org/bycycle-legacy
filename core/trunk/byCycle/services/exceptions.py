################################################################################
# $Id$
# Created 2005-??-??.
#
# byCycle Exceptions.
#
# Copyright (C) 2006 Wyatt Baldwin, byCycle.org <wyatt@bycycle.org>.
# All rights reserved.
#
# For terms of use and warranty details, please see the LICENSE file included
# in the top level of this distribution. This software is provided AS IS with
# NO WARRANTY OF ANY KIND.
################################################################################
"""byCycle Exception."""


class ByCycleError(Exception):
    def __init__(self, desc='byCycle Error'):
        self.description = desc
        Exception.__init__(self)
    def __str__(self):
        return str(self.description)


class InputError(ByCycleError):
    def __init__(self, errors=[]):
        if isinstance(errors, basestring):
            errors = [errors]
        self.errors = errors
        desc = '\n'.join([str(e) for e in errors])
        ByCycleError.__init__(self, desc=desc)


class NotFoundError(ByCycleError):
    pass


class IdentifyError(ByCycleError):
    def __init__(self, desc):
        ByCycleError.__init__(self, desc=desc)