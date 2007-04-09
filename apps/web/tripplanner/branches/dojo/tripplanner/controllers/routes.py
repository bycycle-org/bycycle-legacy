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
                self.q = q
                self.title = 'Whoops!'
                self.errors = "That doesn't look like a route"
                self.action = 'index'
                return self.index()
        else:
            s = request.params.get('s', '').strip()
            e = request.params.get('e', '').strip()
            if s and e:
                q = [s, e]
            else:
                self.title = 'Whoops!'
                if s:
                    self.s = s
                    self.errors = 'Please enter an end address'
                elif e:
                    self.e = e
                    self.errors = 'Please enter a start address'
                else:
                    self.errors = 'Please enter something to search for'
                self.action = 'index'
                return self.index()
        self.s, self.e = q[0], q[1]
        self.q = '%s to %s' % (q[0], q[1])
        params = {}
        for p in ('pref', 'tmode'):
            if p in request.params:
                params[p] = request.params[p]
        def block(exc):
            try:
                raise exc
            except MultipleMatchingAddressesError, exc:
                self._template = '300'
                self.http_status = 300
                self.title = 'Multiple Matches'
                self.choices = exc.choices
        return super(RoutesController, self)._find(q, service_class=Service,
                                                   block=block)
