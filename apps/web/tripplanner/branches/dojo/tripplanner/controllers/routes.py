from byCycle.services.route import Service, MultipleMatchingAddressesError

from tripplanner.controllers.services import *


class RoutesController(ServicesController):
    """Controller for interfacing with byCycle Route service."""

    def find(self):
        q = request.params.get('q', None)
        if q is not None:
            q = self._makeRouteList(q)
        else:
            s = request.params.get('s', None)
            e = request.params.get('e', None)
            q = [s, e]
        c.s, c.e = q[0], q[1]
        c.q = '%s to %s' % (c.s, c.e)
        params = {}
        for p in ('pref', 'tmode'):
            if p in request.params:
                params[p] = request.params[p]
        def block(exc):
            try:
                raise exc
            except MultipleMatchingAddressesError, exc:
                template = '300'
                c.http_status = 300
                c.title = 'Multiple Matches Found'
                self.routes = exc.choices
            return template
        return super(RoutesController, self)._find(q, service_class=Service,
                                                   block=block)
