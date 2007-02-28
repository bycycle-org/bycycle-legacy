import time
import re
import simplejson

from byCycle.services.exceptions import *

from tripplanner.lib.base import *
from tripplanner.controllers.rest import RestController


class ServicesController(RestController):
    """Base class for controllers that interact with back end services."""

    def show(self, query, region, service_class=None, **params):
        """Show the result of ``query``ing a service.

        Subclasses should return this method. In other words, they should
        call this and return the result... unless a service-specific
        ByCycleError is encountered, in which case control should return to
        the subclass to handle the error and render the result.

        ``query``
            Query in form that back end service understands

        ``region``
            Name of region to perform query in

        ``service_class``
            Back end service subclass (e.g., route.Service)

        ``params``
            Optional service-specific parameters
            E.g., for route, tmode=bike, pref=safer

        """
        query = query or request.params.get('q', None)
        self.service = service_class(region=region)
        self.format = request.params.get('format', 'html')
        self.message = ''
        self.results = []

        try:
            self.results = [self.service.query(query, **params)]
        except InputError, exc:
            c.title = 'Error%s' % (['', 's'][len(exc.errors) != 1])
            self.http_status = 400
        except NotFoundError, exc:
            c.title = 'Not Found'
            self.http_status = 404
        except ByCycleError:
            # Let subclass deal with any other `ByCycleError`s
            self.service = service
            self.format = format
            raise
        except Exception, exc:
            c.title = 'Error'
            exc.description = str(exc)
            self.http_status = 500
        else:
            self.template = self.service.name
            self.http_status = 200
            c.title = self.service.name.title()

        try:
            # Was there an error?
            exc
        except UnboundLocalError:
            pass
        else:
            self.message = exc.description
            self.template = 'error'
            c.classes = 'errors'
            c.error_msg = self.message

        # Get rid of this; there is no single result
        # Set an HTML frag for each result
        try:
            self.result = self.results[0]
        except IndexError:
            self.result = None
            
        return self._get_response()

    def _makeRouteList(self, q):
        """Try to parse a route list from the given query, ``q``.

        The query can be . A ValueError is raised if query
        can't be parsed as a list of at least two strings.

        ``q``
            Either a string with waypoints separated by ' to ' or a string
            that will eval as a list

        return
            A list of route waypoints

        raise `ValueError`
            Query can't be parsed as a list of two or more items

        """
        try:
            route_list = eval(q)
        except:
            sRe = '\s+to\s+'
            oRe = re.compile(sRe, re.I)
            route_list = re.split(oRe, q)
        if not (isinstance(route_list, list) and len(route_list) > 1):
            raise ValueError(
                '%s cannot be parsed as a list of two or more items.' % q
            )
        return route_list