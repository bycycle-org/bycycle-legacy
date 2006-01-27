import os, sys


class RestError(Exception): pass
    
class BadRequestError(RestError):
    def __init__(self, reason='Bad Request'):
        self.status = 400
        self.reason = reason

class NotFoundError(RestError):
    def __init__(self, reason='Not Found'):
        self.status = 404
        self.reason = reason

class MultipleChoicesError(RestError):
    def __init__(self, reason='Multiple Choices', choices=None):
        self.status = 300
        self.reason = reason
        self.choices = choices

class MethodNotAllowedError(RestError):
    def __init__(self):
        self.status = 405
        self.reason = 'Method Not Allowed'

    def getAllowMethods(self, restws):
        allow = []
        for method, name in zip((restws.GET, restws.POST,
                                 restws.PUT, restws.DELETE),
                                ("GET", "POST", "PUT", "DELETE")):
            try:
                method()
            except MethodNotAllowedError:
                pass
            else:
                allow.append(name)
        return allow


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
    def __init__(self, **params):
        self.params = params
        
    def GET(self):
        raise MethodNotAllowedError

    def POST(self):
        raise MethodNotAllowedError

    def PUT(self):
        raise MethodNotAllowedError

    def DELETE(self):
        raise MethodNotAllowedError

