import time
import re
import simplejson
from byCycle.services.exceptions import *
from tripplanner.lib.base import *
from tripplanner.controllers.rest import RestController
from tripplanner.controllers.region import RegionController


class ServiceController(RestController):
    """Base class for controllers that interact with back end services."""

    #----------------------------------------------------------------------
    def show(self, query, region, service_class=None, **params):
        """Show the result of ``query``ing a service.

        Subclasses should call return this method. In other words, they should
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

    #----------------------------------------------------------------------
    def _get_response(self):
        """Render response after query to service.

        Return the appropriate type of response according to ``format``.
        ``format`` may be one of "frag" (or "fragment"), "json", or "html"
        (default). "json" will return a JSON object. "html" will return a
        complete HTML template with the result filled in.

        ``service`` `Service`
            A back end service object.

        ``template`` `str`
            Name of template to render.

        ``format``
            Format of response content: html (default), fragment, or json.

        ``http_status`` `int`
            HTTP status code.

        ``message`` `str`
            A message describing the result or an error message.

        ``results`` `list`
            A list of results returned from the back end service. Empty on
            error.

        return `WSGIResponse`

        """
        template = '/service/%s.myt' % self.template
        self.fragment = render(template, oResult=self.result)
        resp = getattr(self, '_get_%s_response' % self.format)()
        resp.status_code = self.http_status
        return resp

    #----------------------------------------------------------------------
    def _get_text_response(self):
        text = render('/service/%s.txt.myt' % self.template, 
                      oResult=self.result)
        resp = Response(content=text, mimetype='text/plain')
        return resp
    
    #----------------------------------------------------------------------
    def _get_json_response(self):
        simple_obj = {
            'type': self.service.name,
            'message': self.message,
            'results': [r.__simplify__() for r in self.results],
            'fragment': self.fragment,
        }
        json = simplejson.dumps(simple_obj)
        resp = Response(content=json, mimetype='text/json')
        return resp

    #----------------------------------------------------------------------
    def _get_html_response(self):
        region_key = self.service.region.key or 'all'
        
        c.region_key = region_key
        c.http_status = self.http_status
        c.service = self.service

        if self.http_status == 200:
            c.result = self.fragment
        else:
            c.errors = self.fragment

        c.info = '\n'
        c.help = None

        region_controller = RegionController()
        resp = region_controller.show(region_key, self.service.name)
        return resp

    #----------------------------------------------------------------------
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
