"""
$$$
:File: feedbackhandler.py
:Description: A class for handling info and error messages
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

class FeedbackHandler(object):

    def __init__(self):
        self.errors = []
        self.messages = []


    def hasError(self): return bool(self.errors)
    def hasMessage(self): return bool(self.messages)


    def addError(self, *args, **kwargs):
        """See addFeedBack for args and kwargs."""
        self.addFeedback("errors", *args, **kwargs)
        
    def addMessage(self, *args, **kwargs):
        """See addFeedBack for args and kwargs."""
        self.addFeedback("messages", *args, **kwargs)

    def addFeedback(self, which, feedback, attop=False):
        attr = self.__dict__[which]
        if not feedback: return
        if type(feedback) == type("str"):
            if attop: attr = [feedback] + attr
            else: attr.append(feedback)
        if type(feedback) == type([]):
            if attop: attr = feedback + attr
            else: attr += feedback


    def processErrors(self, **kwargs):
        """See processFeedback for args and kwargs."""
        return self.processFeedback("errors", **kwargs)

    def processMessages(self, **kwargs):
        """See processFeedback for args and kwargs."""
        return self.processFeedback("messages", **kwargs)

    def processFeedback(self, which, dictionary={}, heading="\nFeedback\n\n",
                        before="", after="\n", ending=""):
        attr = self.__dict__[which]
        if attr:
            feedback = [heading]
            for fb in attr:
                if dictionary:
                    try: fb = dictionary[fb]
                    except KeyError: pass  # fb = fb
                feedback += [''.join((before, fb, after))]
            feedback += [ending]
            feedback = ''.join(feedback)
        else:
            feedback = ""
        return feedback
