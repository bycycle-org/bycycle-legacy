from tripplanner.lib.base import *
from byCycle.model import regions
from tripplanner.controllers.rest import RestController


class RegionsController(RestController):

    def __before__(self):
        """Do stuff before main action is invoked."""
        # Default template context
        c.http_status = 'null'
        c.service = 'query'
        c.region_key = 'all'

    def show(self, id, format=None):
        """Show the ``region`` named ``id``."""
        # Get region key for region
        try:
            region_key = regions.getRegionKey(id)
        except ValueError:
            c.errors = 'Unknown region: %s' % id
            redirect_to('/')
            
        c.region_key = region_key
        c.region_options = self._makeRegionOptions()

        return render_response('/%s/%s.html' % 
                               (self.collection_name, region_key))

    def query(self):
        pass

    def _makeRegionOptions(self):
        """Make list of (display text, value) tuples for HTML options list.

        return -- A list of (display text, value) pairs

        """
        options = []
        # TODO: We should get these from a central location (I think the back
        #       end contains a list of regions, or it could be added to the
        #       existing regions module or to a DB table.)
        state_cities = {
            'or': ['portland',],
            'wi': ['milwaukee',],
        }
        states = state_cities.keys()
        states.sort()
        for state in states:
            cities = state_cities[state]
            cities.sort()
            for city in cities:
                value = '%s%s' % (city, state)
                display_text = '%s, %s' % (city.title(), state.upper())
                options.append((display_text, value))
        return options
