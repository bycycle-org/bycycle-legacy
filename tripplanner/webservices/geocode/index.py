#!/usr/local/bin/python2.4
# Geocode Web Service

from byCycle.lib import wsrest
from byCycle.tripplanner.services import geocode, excs

class Geocode(wsrest.RestWebService):
    def __init__(self):
        wsrest.RestWebService.__init__(self)
                
    def GET(self):
        try:
            geocodes = geocode.get(self.input)
        except excs.InputError, e:
            raise wsrest.BadRequestError(reason=e.description)
        except geocode.AddressNotFoundError, e:
            raise wsrest.NotFoundError(reason=e.description)
        except geocode.MultipleMatchingAddressesError, e:
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
            result = wsrest.ResultSet('geocode', geocodes)
            return repr(result)

Geocode()
