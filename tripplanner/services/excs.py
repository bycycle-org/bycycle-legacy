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
    err = InputError(['fr required', 'region req'])
    print err
    errs = err.getErrors()
    reason = ', '.join(errs)
    print reason
