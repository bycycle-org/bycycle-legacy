import re

from byCycle.services.exceptions import *
from byCycle.model.geocode import Geocode

from tripplanner.lib.base import *
from tripplanner.lib.base import __all__ as base__all__

from tripplanner.controllers.regions import RegionsController

__all__ = base__all__ + ['ServicesController']


class ServicesController(RestController):
    """Base class for controllers that interact with back end services."""

    def __before__(self):
        # Set default region context
        RegionsController._set_default_context()

        # Override default region context
        c.service = self.collection_name

    def find(self):
        """Generic find method. Expects ``q`` to be set in GET params.

        All this does is see if the value of ``q`` looks like a route
        (something like "123 Main St to 616 SW Pants Ave"); if it does,
        redirect to the route controller's ``find``; otherwise, redirect to
        the geocode controller's ``find``.

        """
        q = request.params.get('q', '').strip()
        if q:
            try:
                # See if query looks like a route
                request.params['q'] = self._makeRouteList(q)
            except ValueError:
                # Doesn't look like a route; assume it's a geocode
                self.q = q
                controller = 'geocodes'
            else:
                controller = 'routes'
        else:
            s = request.params.get('s', '').strip()
            e = request.params.get('e', '').strip()
            if s or e:
                controller = 'routes'
            else:
                self.errors = 'Please enter something to search for'
                self.action = 'index'
                return self.index()
        redirect_to('/regions/%s/%s;find' % (self.region.slug, controller),
                    **dict(request.params))

    def _find(self, query, service_class, block=None, **params):
        """Show the result of ``query``ing a service.

        Subclasses should return this method. In other words, they should call
        this and return the result... unless a service-specific ByCycleError
        is encountered, in which case control should return to the subclass to
        handle the error and render the result.

        ``query``
            Query in form that back end service understands

        ``service_class``
            Back end service subclass (e.g., route.Service)

        ``params``
            Optional service-specific parameters
            E.g., for route, tmode=bike, pref=safer

        """
        service = service_class(region=self.region.slug)

        try:
            result = service.query(query, **params)
        except InputError, exc:
            self.http_status = 400
            self.title = 'Error%s' % ('s' if len(exc.errors) != 1 else '')
        except NotFoundError, exc:
            self.http_status = 404
            self.title = 'Not Found'
        except ByCycleError, bc_exc:
            # Let subclass deal with any other `ByCycleError`. The ``block``
            # function should set ``self.http_status`` and ``self.title`` and
            # pass back the name of a template by setting ``self._template``.
            if not block:
                raise
            block(bc_exc)
            template = self._template
        except Exception, exc:
            self.http_status = 500
            self.title = 'Error'
            exc.description = str(exc)
        else:
            self.http_status = 200
            self.title = service.name.title()
            try:
                # Is the result a collection? Note that member objects should
                # not be iterable!
                result[0]
            except TypeError:
                # No, it's a single object (AKA member)
                self.member = result
                template = 'show'
            else:
                # Yes
                self.collection = result
                template = 'index'

        try:
            # Was there an error?
            exc
        except UnboundLocalError:
            pass
        else:
            template = 'index'
            self.errors = exc.description

        return self._render_response(template=template, code=self.http_status)

    def _get_html_content(self, json=True):
        if json:
            self.json = self._get_json_content()[0]
        return super(ServicesController, self)._get_html_content()

    def _get_json_content(self, fragment=True):
        """Get a JSON string.

        Assumes members have a ``__simplify__`` method. Modifies the base
        simple object before JSONification by "wrapping" it in a result
        container object.

        """
        def block(obj):
            result = {
                'type': self.Entity.__class__.__name__,
                'title': getattr(self, 'title', ''),
                'message': getattr(self, 'message', ''),
                'errors': getattr(self, 'errors', ''),
                'results': (obj if isinstance(obj, list) else [obj]),
            }
            if fragment:
                wrap = self.wrap
                self.wrap = False
                f = super(ServicesController, self)._get_html_content()[0]
                self.wrap = wrap
                result['fragment'] = f
            # ``choices`` may be set when HTTP status is 300
            choices = []
            for choice in getattr(self, 'choices', []):
                if isinstance(choice, Geocode):
                    choices.append(choice.__simplify__())
                else:
                    choices.append([m.__simplify__() for m in choice])
            if choices:
                result['choices'] = choices
            return result
        return super(ServicesController, self)._get_json_content(block=block)

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
