import sys
sys.path.insert(0, '/home/bycycle/byCycle/evil')
import re
import simplejson
from tripplanner.lib.base import *
from byCycle.services import exceptions


class RootController(BaseController):
    def __before__(self):
        self.s = request.params.get('s', None)
        self.e = request.params.get('e', None)
        self.format = request.params.get('format', 'html')

    def index(self):
        c.region_options = self._makeRegionOptions()
        return render_response('/tripplanner.myt')

    def query(self, region, query):
        """Prepare query and dispatch to specific service.
        
        ``region`` `str` -- The geographic region selected by the user; this
        parameter may be empty, as long as the region is determinable from
        query (i.e., the query must include city and state and/or zip code).

        ``query`` `str` -- The user's input to the back end service        
        
        return `WSGIResponse`
        
        """
        query = query or request.params.get('q', '')
        try:
            service_method, query = self._analyzeAndPrepareQuery(query)
        except ValueError, exc:
            # TODO: Should return a template with the error displayed OR a JSON 
            # error object ("error": "blah blah")
            # Note: This is a "short-circuit" error-catcher for common errors 
            # (lack of query, unknown service, etc)
            return Response(str(exc))
        else:
            return service_method(region, query)
        
    def geocode(self, region, query):
        from byCycle.services import geocode
        query = query or request.params.get('q', '')
        try:
            c.geocode = geocode.get(query, region)[0]
        except geocode.AddressNotFoundError, exc:
            c.error_msg = exc.description
            return render_response('/not_found.myt', code=404)
        except geocode.MultipleMatchingAddressesError, exc:
            c.geocodes = exc.geocodes
            return render_response('/geocodes.myt', code=300)
        except excs.InputError, exc:
            c.error_msg = exc.description
            return render_response('/error.myt', code=400)
        except Exception, exc:
            c.error_msg = str(exc)
            return render_response('/error.myt', code=500)
        return render_response('/geocode.myt')

    def route(self, region, query):
        from byCycle.services import route
        query = query or [request.params.get('fr', ''), 
                          request.params.get('to', '')]
        try:
            c.route = route.get(region, query)[0]
        except route.NoRouteError, exc:
            c.error_msg = exc.description
            return render_response('/not_found.myt', code=404)            
        except route.MultipleMatchingAddressesError, exc:
            choices = exc.route
            return Response('Multiple Matches for Route', code=300)
        except excs.InputError, exc:
            c.error_msg = exc.description
            return render_response('/error.myt', code=400)
        except Exception, exc:
            c.error_msg = str(exc)
            return render_response('/error.myt', code=500)
        return render_response('/route.myt')
    
    def _makeRegionOptions(self, region=''):
        options = []
        template = '<option value="%s"%s>%s</option>'
        regions = {
            'or': ['portland',],
            'wi': ['milwaukee',],
            'pa': ['pittsburgh',],
            'wa': ['seattle',],
        }
        states = regions.keys()
        states.sort()
        for state in states:
            areas = regions[state]
            areas.sort()
            for area in areas:
                reg = '%s%s' % (area, state)
                proper_region = '%s, %s' % (area.title(), state.upper())
                if reg == region:
                    selected = ' selected="selected"'
                else:
                    selected = ''
                options.append(template % (reg, selected, proper_region))
        return '\n\t\t'.join(options)
    
    def _analyzeAndPrepareQuery(self, query):
        """Analyze generic input query and prepare it for back end service.
        
        ``query`` The user's query string (an address, route, etc)
        ``query`` string
        
        return`` service method object, query string
        
        raise `ValueError`
            - Query is empty
            - Service is unknown
        
        """
        query = ' '.join(query.split())
        if not query:
            raise ValueError('Please enter a query')
        try:
            # See if query looks like a route
            query = self._makeRouteList(query)
        except ValueError:
            # query doesn't look like a route; assume it's a geocode 
            service = 'geocode'
        else:
            service = 'route'                        
        service_method = getattr(self, service)
        return service_method, query
  
    def _makeRouteList(self, query):
        """Try to parse a route list from the given query.
        
        The query can be either a string with waypoints separated by ' to ' or 
        a string that will eval as a list. A ValueError is raised if query 
        can't be parsed as a list of at least two strings.
        
        ``query`` `string` -- User's input query
        
        return [`str`] -- A list of route waypoints
        
        raise `ValueError` Query can't be parsed as a list of two or more items
        
        """
        try:
            route_list = eval(query)
        except:
            sRe = '\s+to\s+'
            oRe = re.compile(sRe, re.I)
            route_list = re.split(oRe, query)
        if isinstance(route_list, list) and len(route_list) > 1:
            service = 'route'
        else:
            raise ValueError('%s cannot be parsed as a list of two or more '
                             'items' % query)
        return route_list
    