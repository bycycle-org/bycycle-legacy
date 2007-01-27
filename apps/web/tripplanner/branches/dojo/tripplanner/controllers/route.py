from byCycle.services.route import Service, MultipleMatchingAddressesError
from byCycle.model.geocode import Geocode
from tripplanner.lib.base import *
from tripplanner.controllers.service import ServiceController


class RouteController(ServiceController):
    """Controller for handling route queries."""

    #----------------------------------------------------------------------
    def show(self, query, region):
        query = self._makeRouteList(query)
        c.s, c.e = query[0], query[1]
        c.q = '%s to %s' % (c.s, c.e)
        params = {}
        for p in ('pref', 'tmode'):
            if p in request.params:
                params[p] = request.params[p]
        try:
            return super(RouteController, self).show(
                query, region, service_class=Service, **params
            )
        except MultipleMatchingAddressesError, exc:
            template = 'route_geocodes'
            results = exc.choices
            http_status = 300
            c.title = 'Multiple Matches Found'
            c.classes = 'errors'
        # We'll get here only if there's an unhandled error in the superclass.
        # Otherwise, the superclass will handle rendering directly.
        return self._get_response(
            self.service, template, http_status, self.format, results=results
        )
