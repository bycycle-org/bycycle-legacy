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
        content = exc.reason + ' (%s)' % method
        req.allow_methods(exc.getAllowMethods(self))
    except wsrest.MultipleChoicesError, exc:
        reason = exc.reason
        content = exc.choices
    except wsrest.RestError, exc:
        content = exc.reason
    except Exception, exc:
        status = 500
        content = str(exc)
    else:
        status = 200

    try:
        req.status = exc.status
    except (NameError, AttributeError):
        req.status = status
    
    req.content_type = 'text/plain'
    return content


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

    doRequest(geocode, region='milwaukeewi', q='27th and lisbon')
    doRequest(route, region='milwaukeewi', tmode='bike',
              q="['35th and north', '124 and county line']")
    doRequest(route, region='milwaukeewi', tmode='bike',
              q="['35th and north', '27th and lisbon']")
