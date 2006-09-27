###########################################################################
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


class ByCycleError(Exception):
    def __init__(self, desc='byCycle Error'): 
        self.description = desc
    def __str__(self):
        return str(self.description)

        
class InputError(ByCycleError):
    def __init__(self, errors=[]):
        desc = '\n'.join([str(e) for e in errors])
        ByCycleError.__init__(self, desc=desc)
