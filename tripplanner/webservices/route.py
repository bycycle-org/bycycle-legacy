# Route Web Service

from byCycle.lib import wsrest
from byCycle.tripplanner.services import route

class Route(wsrest.RestWebService):
    def __init__(self):
        wsrest.RestWebService.__init__(self)
             
    def GET(self):
        try:
            q = self.input['q'].replace('\n', ' ')
            self.input['q'] = eval(q)
            the_route = route.get(self.input)
        except route.InputError, e:
            raise wsrest.BadRequestError(reason=e.description)
        except route.MultipleMatchingAddressesError, e:
            self.status = '300'
            self.reason = e.description
            result = wsrest.ResultSet('geocode', e.geocodes)
            return repr(result)            
        except Exception, e:
            #import time
            #log = open('error_log', 'a')
            #log.write('%s: %s\n' % (time.asctime(), e))
            #log.close()
            raise
        else:
            result = wsrest.ResultSet('route', the_route)
            return repr(result)
