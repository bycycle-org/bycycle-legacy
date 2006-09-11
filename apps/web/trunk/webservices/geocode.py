"""$Id: geocode.py 190 2006-08-16 02:29:29Z bycycle $

Geocode Web Service.

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
from byCycle.lib import wsrest
from byCycle.tripplanner.services import excs, geocode

class Geocode(wsrest.RestWebService):
    def __init__(self, **params):
        wsrest.RestWebService.__init__(self, **params)
                
    def GET(self):
        try:
            geocodes = geocode.get(**self.params)
        except excs.InputError, exc:
            raise wsrest.BadRequestError(reason=exc.description)
        except geocode.AddressNotFoundError, exc:
            raise wsrest.NotFoundError(reason=exc.description)
        except geocode.MultipleMatchingAddressesError, exc:
            choices = repr(wsrest.ResultSet('geocode', exc.geocodes))
            raise wsrest.MultipleChoicesError(reason=exc.description,
                                              choices=choices)
        except Exception, exc:
            raise
        else:
            return repr(wsrest.ResultSet('geocode', geocodes))
