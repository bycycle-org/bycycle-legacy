"""$Id$

Description goes here.

Copyright (C) 2006 Wyatt Baldwin, byCycle.org <wyatt@bycycle.org>

All rights reserved.

TERMS AND CONDITIONS FOR USE, MODIFICATION, DISTRIBUTION

1. The software may be used and modified by individuals for noncommercial, 
private use.

2. The software may not be used for any commercial purpose.

3. The software may not be made available as a service to the public or within 
any organization.

4. The software may not be redistributed.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND 
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED 
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE 
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR 
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES 
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; 
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON 
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT 
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS 
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
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
