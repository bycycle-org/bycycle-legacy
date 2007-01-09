from tripplanner.lib.base import *
from tripplanner.controllers.service import ServiceController
from tripplanner.controllers.geocode import GeocodeController
from tripplanner.controllers.route import RouteController


class QueryController(ServiceController):
    """Controller for handling generic queries."""

    #----------------------------------------------------------------------
    def index(self):
        """Redirect to `show`."""
        q = request.params.get('q', None)
        if q is not None:
            self.show(q)
        else:
            return Response('Query with no arg.')

    #----------------------------------------------------------------------
    def show(self, query, region=None):
        """Prepare ``query`` and redirect to a specific service.

        ``query`` `str` -- The user's input to the back end service.
        ``region`` `str` -- Geographic region

        return `WSGIResponse`

        """
        query = [query, None][query == ':q'] or request.params.get('q', None)
        try:
            controller, query = self._analyzeAndPrepareQuery(query)
        except ValueError, exc:
            # TODO: Should return a template with the error displayed OR and
            # HTML error fragment OR a JSON error object ("error": "blah
            # blah"). Note: This is a "short-circuit" error-catcher for common
            # errors (lack of query, unknown service, etc).
            return Response(str(exc))
        else:
            params = dict(request.params)
            try:
                del params['q']
            except KeyError:
                pass
            redirect_to('/%s/%s/%s' % (region, controller, query), **params)

    #----------------------------------------------------------------------
    def _analyzeAndPrepareQuery(self, q):
        """Analyze generic input query and prepare it for back end service.

        ``q`` `string` The user's query string (an address, route, etc)

        return service, prepared query string

        raise `ValueError`
            - Query is empty
            - Service is unknown

        """
        _q = ' '.join(q.split())
        if not _q:
            raise ValueError('Please enter an address, intersection, or route')
        try:
            # See if query looks like a route
            _q = self._makeRouteList(_q)
        except ValueError:
            # ``q`` doesn't look like a route; assume it's a geocode
            service = 'geocode'
        else:
            service = 'route'
        return service, _q
