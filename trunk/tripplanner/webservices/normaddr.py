# Address Normalization Web Service

from byCycle.lib import wsrest
from byCycle.tripplanner.services import normaddr

class Normaddr(wsrest.RestWebService):
    def __init__(self, **params):
        wsrest.RestWebService.__init__(self, **params)
        
    def GET(self): 
        try:
            address = normaddr.get(**self.params)
        except Exception, e:
            raise e
        else:
            return repr(wsrest.ResultSet('normaddr', address))
