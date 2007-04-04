from byCycle.model import regions

from tripplanner.lib.base import *


class RegionsController(RestController):

    def __before__(self):
        self._set_default_context()

    def index(self):
        # legacy support
        params = dict(request.params)
        prefix = 'bycycle_'
        for k in params:
            if k.startswith(prefix):
                params[k.lstrip(prefix)] = params.pop(k)
        id = params.pop('region', '')
        if id:
            if 'q' in params or 'fr' in params or 'to' in params:
                redirect_to('find_services', region_id=id, **params)
            else:
                redirect_to('region', id=id, **params)
        else:
            return super(RegionsController, self).index()

    def show(self, id):
        """Show the ``region`` with ID or name or key ``id``."""
        id = self._get_region_id(id)
        return super(RegionsController, self).show(id)

    def find(self):
        params = dict(request.params)
        region = params.pop('region', None)
        if not region:
            self.action = 'index'
            c.q = params.get('q', '')
            return self.index()
        elif params.get('q').strip():
            redirect_to('find_services', region_id=region, **params)
        else:
            redirect_to('region', id=region)

    @staticmethod
    def _set_default_context():
        """Set default template context."""
        c.service = 'services'
        c.region_options = RegionsController._makeRegionOptions()

    @staticmethod
    def _get_region_id(region_id):
        try:
            return long(region_id)
        except (ValueError, TypeError):
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
