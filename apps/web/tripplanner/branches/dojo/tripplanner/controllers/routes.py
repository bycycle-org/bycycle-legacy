from byCycle.services.route import Service, MultipleMatchingAddressesError

from tripplanner.controllers.services import *


class RoutesController(ServicesController):
    """Controller for interfacing with byCycle Route service."""

    def find(self):
        q = request.params.get('q', '').strip()
        if q:
            try:
                q = self._makeRouteList(q)
            except ValueError:
                c.title = 'Whoops!'
                c.errors = "That doesn't look like a route"
                self.template = 'index'
                return self.index()
        else:
            s = request.params.get('s', '').strip()
            e = request.params.get('e', '').strip()
            if s and e:
                q = [s, e]
            else:
                c.title = 'Whoops!'
                if s:
                    c.errors = 'Please enter an end address'
                elif e:
                    c.errors = 'Please enter a start address'
                else:
                    c.errors = 'Please enter something to search for'
                self.template = 'index'
                return self.index()
        c.s, c.e = q[0], q[1]
        c.q = '%s to %s' % (q[0], q[1])
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
