# Route Web Service

from byCycle.lib import wsrest
from byCycle.tripplanner.services import excs, route

class Route(wsrest.RestWebService):
    def __init__(self, **params):
        wsrest.RestWebService.__init__(self, **params)
        
    def GET(self): 
        try:
            the_route = route.get(**self.params)
        except excs.InputError, exc:
            raise wsrest.BadRequestError(reason=exc.description)
        except route.MultipleMatchingAddressesError, exc:
            choices = repr(wsrest.ResultSet('route', exc.route))
            raise wsrest.MultipleChoicesError(reason=exc.description,
                                              choices=choices)
        except Exception:
            raise
        else:
            return repr(wsrest.ResultSet('route', the_route))
