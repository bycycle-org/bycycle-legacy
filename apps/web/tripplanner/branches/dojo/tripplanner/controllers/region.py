from tripplanner.lib.base import *
from byCycle.model import regions
from tripplanner.controllers.view import ViewController


class RegionController(ViewController):

    def __before__(self):
        # Default template context
        #c.region_title = 'All Regions'
        c.http_status = 'null'
        c.service = 'query'
        c.region_key = 'all'

    def index(self):
        c.regions = []  # Get all regions from DB
        return render_response('/regions/index.html')

    def show(self, region):
        """Show ``region``."""
        # IF   region = Region.find(params[:id])
        # ELSE region = Region.find_by_name(params[:id])

        # Region not given in URL path; see if it's given as a query param
        # TODO: Maybe there should be some middleware to convert old-style
        #       URLs to the new Routes???
        if region is None:
            region = request.params.get('region', None)
            if region is not None:
                redirect_to('/%s' % region)

        # Get region key for region
        try:
            region_key = regions.getRegionKey(region)
        except ValueError:
            # Bad/unknown region
            # TODO: Show an error instead of just showing all regions
            region_key = 'all'
            c.errors = 'Unknown region: %s' % region

        c.region_key = region_key
        c.region_options = self._makeRegionOptions()

        return render_response('/region/show.myt')  # /region/%s.html % region_key

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
