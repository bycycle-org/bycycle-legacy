# Web Services Index

def geocode(req, **params):
    from byCycle.tripplanner.webservices import geocode
    service = geocode.Geocode(**params)
    return _process(req, service)


def route(req, **params):
    from byCycle.tripplanner.webservices import route
    service = route.Route(**params)
    return _process(req, service)


def _process(req, service):
    try: 
        from mod_python import apache
    except ImportError:
        pass
    from byCycle.lib import wsrest
    
    method = req.method
    try:
        content = eval('service.%s' % method)()
    except wsrest.MethodNotAllowedError, exc:
        reason = exc.reason + ' (%s)' % method
        req.allow_methods(exc.getAllowMethods(self))
    except wsrest.MultipleChoicesError, exc:
        reason = exc.reason
        content = exc.choices
    except wsrest.RestError, exc:
        reason = exc.reason
    except Exception, exc:
        status = 500
        reason = 'Internal Server Error (%s)' % str(exc)
    else:
        status = 200
        reason = 'OK'

    try:
        req.status = exc.status
        req.reason = exc.reason
    except (NameError, AttributeError):
        req.status = status
        req.reason = reason
    
    req.content_type = 'text/plain'
    try:
        return content
    except NameError:
        return ''


if __name__ == '__main__':
    class Req(object):
        def __init__(self):
            self.content_type = ''
            self.headers_out = {}

    def doRequest(service, **params):
        req = Req()
        req.method = 'GET'
        content = service(req, **params)
        print req.content_type
        print req.headers_out
        print req.status

        #print req.reason
        print content
        print

    #doRequest(geocode, region='milwaukee', q='124 and county line')
    doRequest(route, region='milwaukee', tmode='bike',
              q="['35th and north', '124 and county line']")
    doRequest(route, region='milwaukee', tmode='bike',
              q="['35th and north', '27th and lisbon']")
