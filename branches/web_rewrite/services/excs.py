"""$Id$

Description goes here.

Copyright (C) 2006 Wyatt Baldwin, byCycle.org <wyatt@bycycle.org>. All rights 
reserved. Please see the LICENSE file included in the distribution. The license 
is also available online at http://bycycle.org/tripplanner/license.txt or by 
writing to license@bycycle.org.

"""


class ByCycleError(Exception):
    def __init__(self, desc='byCycle Error'): 
        self.description = desc
        
    def __str__(self):
        return self.description

        
class InputError(ByCycleError):
    def __init__(self, errors=[]):
        desc = '\n'.join(errors)
        ByCycleError.__init__(self, desc=desc)
