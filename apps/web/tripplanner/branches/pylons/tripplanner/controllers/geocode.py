import time
import simplejson
from byCycle.services.exceptions import *
from byCycle.services.geocode import *
from tripplanner.lib.base import *
from tripplanner.controllers.service import ServiceController



class GeocodeController(ServiceController):
    """Controller for handling geocode queries."""

    #----------------------------------------------------------------------
    def show(self, query, region):
        query = query or request.params.get('q', None)
        format = request.params.get('format', 'html')
        service = Service(region=region)
        try:
            geocode = service.query(query)
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
        except AddressNotFoundError, exc:
            c.error_msg = exc.description
            template = 'not_found'
            code = 404
        except Exception, exc:
            c.error_msg = str(exc)
            template = 'error'
            code = 500
        else:
            template = 'geocode'
            code = 200
            c.geocode = geocode
            c.json = simplejson.dumps(eval(repr(geocode)))
        c.service = service
        c.result_id = ('%.6f' % time.time()).replace('.', '')
        # TODO: Branch according to `format` here and return the appropriate
        # response. The options are: 1) An HTML fragment that will replace the
        # result area of the currently displayed page, 2) A JSON object, or 3)
        # A complete HTML template with the result filled in.
        return render_response('/service/%s.myt' % template, code=code)
