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

    title = 'Error'
    description = 'byCycle Error'

    def __init__(self):
        Exception.__init__(self)

    def __str__(self):
        return str(self.description)


class InputError(ByCycleError):

    title = 'Input Error'
    
    def __init__(self, errors=[]):
        if isinstance(errors, basestring):
            errors = [errors]
        self.errors = errors
        self.description = '\n'.join([str(e) for e in errors])
        ByCycleError.__init__(self)


class NotFoundError(ByCycleError):

    title = 'Not Found'

    def __init__(self):
        ByCycleError.__init__(self)


class IdentifyError(ByCycleError):

    title = 'Unidentifiable'

    def __init__(self):
        ByCycleError.__init__(self)
