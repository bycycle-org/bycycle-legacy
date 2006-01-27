# Geocode Web Service

from byCycle.lib import wsrest
from byCycle.tripplanner.services import geocode

class Geocode(wsrest.RestWebService):
    def __init__(self, **params):
        wsrest.RestWebService.__init__(self, **params)
                
    def GET(self):
        try:
            geocodes = geocode.get(self.params)
        except geocode.InputError, exc:
            raise wsrest.BadRequestError(reason=exc.description)
        except geocode.AddressNotFoundError, exc:
            raise wsrest.NotFoundError(reason=exc.description)
        except geocode.MultipleMatchingAddressesError, exc:
            choices = repr(wsrest.ResultSet('geocode', exc.geocodes))
            raise wsrest.MultipleChoicesError(reason=exc.description,
                                              choices=choices)
        except Exception, exc:
            raise
        else:
            return repr(wsrest.ResultSet('geocode', geocodes))
