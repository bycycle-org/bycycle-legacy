"""$Id$

Geocode model classes.

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
from byCycle.lib import gis

    
class Geocode(object):
    def __str__(self):
        return str(self.address)

    
class PostalGeocode(Geocode):
    def __init__(self, address=None, segment=None, xy=None):
        self.address = address
        self.segment = segment
        self.xy = xy
        self.network_id = self.segment.id
        
    def __repr__(self):
        result = {
            'type': 'postal',
            'number': self.address.number,
            'street': self.address.street,
            'place': self.address.place,
            'address': str(self.address),
            'x': '%.6f' % self.xy.x,
            'y': '%.6f' % self.xy.y,
            'edge_id': self.segment.id,
            'network_id': self.network_id
        }
        return repr(result)

    
class IntersectionGeocode(Geocode):
    def __init__(self, address=None, intersection=None):
        self.address = address
        self.intersection = intersection
        self.xy = intersection.lon_lat
        self.network_id = self.intersection.id

    def __repr__(self):
        result = {
            'type': 'intersection',
            'street1': self.address.street1,
            'street2': self.address.street2,
            'place1': self.address.place1,
            'place2': self.address.place2,
            'address': str(self.address),                  
            'x': '%.6f' % self.xy.x,
            'y': '%.6f' % self.xy.y,
            'node_id': self.intersection.id,
            'network_id': self.network_id         
            }
        return repr(result)
