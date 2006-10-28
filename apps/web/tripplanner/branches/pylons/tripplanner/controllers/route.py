from byCycle.services.route import *
from tripplanner.lib.base import *
from tripplanner.controllers.service import ServiceController


class RouteController(ServiceController):
    """Controller for handling route queries."""

    #----------------------------------------------------------------------
    def show(self, query, region):
        try:
            query = self._makeRouteList(query)
            c.s, c.e = query[0], query[1]
            c.q = '%s to %s' % (c.s, c.e)
            return super(RouteController, self).show(
                query, region, service_class=Service
            )
        except MultipleMatchingAddressesError, exc:
            template = 'geocodes'
            oResult = exc.geocodes
            http_status = 300
            to_json = [eval(repr(g)) for g in oResult]
            c.title = 'Multiple Matches Found'
            c.classes = 'errors'
        # We'll get here only if there's an unhandled error in the superclass.
        # Otherwise, the superclass will handle rendering directly.
        return self._render(
            self.service, template, http_status, self.format, oResult, to_json
        )
