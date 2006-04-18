from byCycle.lib import feedbackhandler


class ByCycleError(Exception):
    def __init__(self, desc=''): 
        if not desc:
            desc = 'byCycle Error'
        self.description = desc

    def __str__(self):
        return self.description

        
class InputError(ByCycleError):
    def __init__(self, errors=[]):
        desc = '\n'.join(errors)
        ByCycleError.__init__(self, desc=desc)

