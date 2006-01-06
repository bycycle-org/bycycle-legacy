"""
$$$
:File: exceptions.py
:Description: Exceptions for the byCycle system
:Author: Wyatt Baldwin
:Copyright: 2005 byCycle.org
:License: GPL
:Version: 0
:Date: 15 Aug 2005
$$$

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
ERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""

from byCycle.lib import feedbackhandler

error_dictionary = {
    # Missing field errors (key same as field name)
    # segment
    }


class Error(Exception):
    def __init__(self, errors=[]):
        self.fh = feedbackhandler.FeedbackHandler()
        self.type = "BycycleError"
        self.description = "byCycle Error"
        if errors: self.addError(errors)

    def addError(self, error, **kwargs):
        self.fh.addError(error, **kwargs)
        
    def getErrorString(self, **kwargs):
        if not self.fh.hasError(): self.addError(self.description)
        return self.fh.processErrors(dictionary=error_dictionary, **kwargs)
    
    def getErrors(self):
        E = []
        for e in self.fh.errors:
            try: E.append(error_dictionary[e])
            except KeyError: E.append(e)
        return E

    def __str__(self): return self.getErrorString()

    def __repr__(self):
        rep = {'error': {'type': self.__class__.__name__,
                         'desc': self.description,
                         'msgs': self.getErrors()}}
        return repr(rep)


class InputError(Error):
    def __init__(self, errors):
        Error.__init__(self, errors) 
        self.description = 'Bad Input'


if __name__ == '__main__':
    err = InputError(['fr required', 'dmode req'])
    print err
    errs = err.getErrors()
    reason = ', '.join(errs)
    print reason
