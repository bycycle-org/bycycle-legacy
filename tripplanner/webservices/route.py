# Route Web Service

from byCycle.lib import wsrest
from byCycle.tripplanner.services import route

class Route(wsrest.RestWebService):
    def __init__(self, **params):
        wsrest.RestWebService.__init__(self, **params)
        
    def GET(self): 
        try:
            q = self.params['q'].replace('\n', ' ')
            self.params['q'] = eval(q)
            the_route = route.get(**self.params)
        except route.InputError, exc:
            raise wsrest.BadRequestError(reason=exc.description)
        except route.MultipleMatchingAddressesError, exc:
            choices = repr(wsrest.ResultSet('geocode', exc.geocodes))
            raise wsrest.MultipleChoicesError(reason=exc.description,
                                              choices=choices)
        except Exception:
            raise
        else:
            return repr(wsrest.ResultSet('route', the_route))
