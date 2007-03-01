from tripplanner.lib.base import *
from byCycle.model import regions
from tripplanner.controllers.rest import RestController


class RegionsController(RestController):

    def __before__(self):
        """Do stuff before main action is invoked."""
        self._set_default_context()
    
    def show(self, id, format=None):
        """Show the ``region`` with ID or name or key ``id``."""
        # Get region key for region
        region_key = self._get_region_key(id)
        c.region_key = region_key
        return self._render_response(format=format, template=region_key)

    @staticmethod
    def _set_default_context():
        """Set default template context."""
        c.service = 'services'
        c.region_key = 'all'
        c.region_options = RegionsController._makeRegionOptions()

    @staticmethod
    def _get_region_key(region_id):
        try:
            return regions.getRegionKey(region_id)
        except ValueError:
            c.errors = 'Unknown region: %s' % region_id
            redirect_to('/regions')

    @staticmethod
    def _makeRegionOptions():
        """Make list of (display text, value) tuples for HTML options list.

        return
            A list of (display text, value) pairs

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
