"""$Id$

A class for handling info and error messages.

Copyright (C) 2006 Wyatt Baldwin, byCycle.org <wyatt@bycycle.org>

All rights reserved.

TERMS AND CONDITIONS FOR USE, MODIFICATION, DISTRIBUTION

1. The software may be used and modified by individuals for noncommercial, 
private use.

2. The software may not be used for any commercial purpose.

3. The software may not be made available as a service to the public or within 
any organization.

4. The software may not be redistributed.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND 
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED 
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE 
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR 
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES 
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; 
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON 
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT 
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS 
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

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
