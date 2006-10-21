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
        json = None
        try:
            geocode = service.query(query)
        except MultipleMatchingAddressesError, exc:
            geocodes = exc.geocodes
            template = 'geocodes'
            http_status = 300
            c.geocodes = geocodes
            json = simplejson.dumps([eval(repr(g)) for g in geocodes])
        except InputError, exc:
            c.error_msg = exc.description
            template = 'error'
            http_status = 400
        except AddressNotFoundError, exc:
            c.error_msg = exc.description
            template = 'not_found'
            http_status = 404
        except Exception, exc:
            c.error_msg = str(exc)
            template = 'error'
            http_status = 500
        else:
            template = 'geocode'
            http_status = 200
            c.geocode = geocode
            json = simplejson.dumps(eval(repr(geocode)))
        return ServiceController._render(
            self, service, template, http_status, format, json
        )
