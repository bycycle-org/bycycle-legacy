from tripplanner.lib.base import *
from tripplanner.controllers.rest import RestController


class ViewController(RestController):
    """Controller for views."""
        
    def index(self, url=None):
        return Response('%s was not found.' % url)
