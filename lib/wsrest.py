import os, cgi, sys


class RestError(Exception): pass
    
class BadRequestError(RestError):
    def __init__(self, reason='Bad Request'):
        self.status = '400'
        self.reason = reason

class NotFoundError(RestError):
    def __init__(self, reason='Not Found'):
        self.status = '404'
        self.reason = reason

class MethodNotAllowedError(RestError):
    def __init__(self):
        self.status = '405'
        self.reason = 'Method Not Allowed'

    def getAllowHeader(self, restws):
        allow = []
        for method, name in zip((restws.GET, restws.POST,
                                 restws.PUT, restws.DELETE),
                                ("GET", "POST", "PUT", "DELETE")):
            try: method()
            except MethodNotAllowedError: pass
            else: allow.append(name)
        return "Allow: %s" % (", ".join(allow))


class ResultSet(object):
    def __init__(self, result_type, result):
        self.result_type = result_type
        self.result = result

    def __repr__(self):
        result_set = {'result_set': {'type': self.result_type,
                                     'result': self.result}}
        return repr(result_set)

    def __len__(self):
        return len(self.result)
    

class RestWebService(object):
    def __init__(self):
        try:
            self.method = os.environ['REQUEST_METHOD']
        except KeyError:
            pass
        else:
            self.input = {}
            input = cgi.FieldStorage()
            for key in input:
                self.input[key.strip()] = input.getfirst(key).strip()

            self.status = '200'
            self.reason = 'OK'
            self.content = ''
            self.content_length = 0

            try:
                self.content = eval("self." + self.method)()
            except MethodNotAllowedError, e:
                self.status = e.status
                self.reason = e.reason + " (%s)" % self.method
                self.headers += e.getAllowHeader(self)
            except RestError, e:
                self.status = e.status
                self.reason = e.reason
            except Exception, e:
                self.status = '500'
                self.reason = 'Internal Server Error (%s)' % str(e)
                
            if not self.content: self.content = self.reason

            if eval(repr(self.content)):
                self.content_length = len(self.content)
            self.headers = ["Status: %s %s" % (self.status,
                                               self.reason),
                            "Content-Type: text/plain",
                            "Content-Length: %s" % self.content_length,
                            "\r\n"]
            sys.stdout.write("\r\n".join(self.headers))            
            sys.stdout.flush()
            if self.content_length: sys.stdout.write(self.content)

    def GET(self): raise MethodNotAllowedError
    def POST(self): raise MethodNotAllowedError
    def PUT(self): raise MethodNotAllowedError
    def DELETE(self): raise MethodNotAllowedError

