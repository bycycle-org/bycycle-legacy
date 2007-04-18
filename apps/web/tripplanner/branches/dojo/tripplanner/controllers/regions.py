from byCycle.model import regions

from tripplanner.lib.base import *


class RegionsController(RestController):

    def __before__(self):
        c.service = 'services'

    def index(self):
        # legacy support
        params = dict(request.params)
        prefix = 'bycycle_'
        for k in params:
            if k.startswith(prefix):
                params[k.lstrip(prefix)] = params.pop(k)
        id = self._get_region_id(params.pop('region', ''), params)
        # KLUDGE: _get_region_id shouldn't return "all" by default
        id = None if id == 'all' else id
        if id:
            if 'fr' in params:
                params['s'] = params.pop('fr')
            if 'to' in params:
                params['e'] = params.pop('to')
            if 'q' in params or 's' in params or 'e' in params:
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
        region_id = params.pop('region', None)
        if region_id is not None:
            region_id = self._get_region_id(region_id)
        q = params.get('q', '').strip()
        params.pop('commit', '')
        if not region_id:
            self.action = 'index'
            self.q = q
            return self._render_response(template='index')
        elif q:
            redirect_to('find_services', region_id=region_id, **params)
        else:
            params.pop('q', '')
            redirect_to('region', id=region_id, **params)

    @staticmethod
    def _get_region_id(region_id, params=None):
        """Normalize ``region_id``."""
        try:
            return long(region_id)
        except (ValueError, TypeError):
            try:
                return regions.getRegionKey(region_id)
            except ValueError:
                c.errors = 'Unknown region: %s' % region_id
                params = params or dict(request.params)
                params.pop('region', '')
                params.pop('bycycle_region', '')
                redirect_to('/regions', **dict(params))
