import simplejson
from byCycle.services.exceptions import *
from byCycle.services.route import *
from tripplanner.lib.base import *
from tripplanner.controllers.service import ServiceController


class RouteController(ServiceController):
    """Controller for handling route queries."""

    #----------------------------------------------------------------------
    def show(self, query, region=None):
        query = query or request.params.get('q', None)
        if query is None:
            query = ('["' + request.params.get('s', '') + '", "' +
                     request.params.get('e', '') + '"]')
        region = request.params.get('region', None)
        format = request.params.get('format', 'html')
        service = Service(region=region)
        try:
            route = service.query(eval(query))
        except MultipleMatchingAddressesError, exc:
            geocodes = exc.geocodes
            template = 'geocodes'
            code = 300
            c.geocodes = geocodes
            c.json = simplejson.dumps([eval(repr(g)) for g in geocodes])
        except InputError, exc:
            c.error_msg = exc.description
            template = 'error'
            code = 400
        except NoRouteError, exc:
            c.error_msg = exc.description
            template = 'not_found'
            code = 404
        except Exception, exc:
            c.error_msg = str(exc)
            template = 'error'
            code = 500
        else:
            template = 'route'
            code = 200
            c.route = route
            c.json = simplejson.dumps(eval(repr(route)))
        c.service = service
        # TODO: Branch according to `format` here and return the appropriate
        # response. The options are: 1) An HTML fragment that will replace the
        # result area of the currently displayed page, 2) A JSON object, or 3)
        # A complete HTML template with the result filled in.
        return render_response('/service/%s.myt' % template, code=code)
