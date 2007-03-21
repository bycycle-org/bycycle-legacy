from byCycle.services.route import Service, MultipleMatchingAddressesError

from tripplanner.lib.base import *
from tripplanner.controllers.services import ServicesController


class RoutesController(ServicesController):
    """Controller for handling route queries."""

    #----------------------------------------------------------------------
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
        try:
            return super(RoutesController, self)._find(
                q, service_class=Service, **params
            )
        except MultipleMatchingAddressesError, exc:
            template = '300'
            c.http_status = 300
            self.collection = exc.choices
        # We'll get here only if there's an unhandled error in the superclass.
        # Otherwise, the superclass will handle rendering.
        return self._render_response(
            format=self.format, template=template, code=c.http_status
        )
