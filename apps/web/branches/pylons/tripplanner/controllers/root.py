from tripplanner.lib.base import *

class RootController(BaseController):
    def index(self):
        """Handle initial site entry, with or without params."""
        # Check for query args
        # If args, sort them out and redirect appropriately
        # If no args, just return base template
        return render_response('/tripplanner.myt')

    def region(self, region=None):
        # Check for a valid region
        # Return region template
        return render_response('/%s.myt' % region)
    
    
    def service(self, region=None, service=None, query=None):
        """Dispatch to service.
        
        If region isn't given, it must be determinable from query (i.e., the
        query must then contain city and state and/or zip code)
        
        """
        # Check for valid region
        # Do some basic checks on service and query
        # Call back end
        # Return region template with result 
        try:
            # Do query to service
            getattr(self, service.lower())()
        except AttributeError:
            # Unknown service, blah blah
            pass
        return render_response('/tripplanner.myt')
    
    def address(self, region=None, query=''):
        c.service = 'address'
        pass

    def geocode(self, region=None, query=''):
        c.poo = 'geocode'
        pass
    
    def route(self, region=None, query=[]):
        c.poo = 'route'
        pass
