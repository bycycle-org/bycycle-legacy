import re

from byCycle.services.exceptions import *

from tripplanner.lib.base import *
from tripplanner.controllers.rest import RestController
from tripplanner.controllers.regions import RegionsController


class ServicesController(RestController):
    """Base class for controllers that interact with back end services."""

    def __before__(self):
        """Do stuff before main action is invoked."""

        # Set default region context
        RegionsController._set_default_context()

        # Override default region context
        c.region_key = RegionsController._get_region_key(self.parent_id)

    def find(self, parent_id=None):
        """Generic find method. Expects a ``q`` query parameter.

        All this does is see if the value of ``q`` looks like a route (something
        like A to B); if it does, redirect to the route controller's find; 
        otherwise, redirect to the geocode controller's find.

        ``region_id``
            Region key or ID

        raise `ValueError`
            - Query is empty
            - Service is unknown

        return `Response`

        """
        query = ' '.join(request.params.get('q', '').split())
        if not query:
            raise ValueError('Please enter an address, intersection, or route')
        try:
            # See if query looks like a route
            request.params['q'] = self._makeRouteList(query)
        except ValueError:
            # Doesn't look like a route; assume it's a geocode
            controller = 'geocodes'
        else:
            controller = 'routes'
        redirect_to('/regions/%s/%s;find' % (parent_id, controller),
                    **dict(request.params))

    def _find(self, query, region_id, service_class, **params):
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
        c.q = query

        service = service_class(region=c.region_key)
        format = request.params.get('format', 'html')
        template = 'show'

        try:
            result = service.query(query, **params)
        except InputError, exc:
            c.http_status = 400
            c.title = 'Error%s' % ('s' if len(exc.errors) != 1 else '')
        except NotFoundError, exc:
            c.http_status = 404
            c.title = 'Not Found'
        except ByCycleError:
            # Let subclass deal with any other `ByCycleError`s
            self.format = format
            self.template = template
            raise
        except Exception, exc:
            c.http_status = 500
            c.title = 'Error'
            exc.description = str(exc)
        else:
            c.http_status = 200
            c.title = service.name.title()
            if isinstance(result, (list, tuple)):
                name = self.collection_name
                template = 'index'
            else:
                name = self.member_name
            self._setattr(name, result)

        try:
            # Was there an error?
            exc
        except UnboundLocalError:
            pass
        else:
            template = 'error'
            c.message = exc.description
            c.classes = 'errors'

        return self._render_response(
            format=format, template=template, code=c.http_status
        )

    def _get_json_content(self):
        """Get a JSON string.

        Assumes members have a __simplify__ method. Modifies the base simple
        object before JSONification by "wrapping" it in a result container
        object.

        """
        def f(obj):
            return {
                'type': self.member_name,
                'message': c.message,
                'results': (obj if isinstance(obj, list) else [obj]),
                'fragment': self._get_fragment_content()[0]
            }
        return super(ServicesController, self)._get_json_content(obj_func=f)

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
