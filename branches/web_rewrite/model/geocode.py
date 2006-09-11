"""$Id$

Geocode classes.

Copyright (C) 2006 Wyatt Baldwin, byCycle.org <wyatt@bycycle.org>. All rights 
reserved. Please see the LICENSE file included in the distribution. The license 
is also available online at http://bycycle.org/tripplanner/license.txt or by 
writing to license@bycycle.org.

"""
from byCycle.lib import gis

    
class Geocode(object):
    def __str__(self):
        return str(self.address)

    
class PostalGeocode(Geocode):
    def __init__(self, address=None, segment=None, xy=None):
        self.address = address
        self.segment = segment
        self.network_id = segment.id
        self.xy = xy
        
    def __repr__(self):
        result = {
            'type': 'postal',
            'number': self.address.number,
            'street': self.address.street,
            'place': self.address.place,
            'address': str(self.address),
            'x': '%.6f' % self.xy.x,
            'y': '%.6f' % self.xy.y,
            'network_id': self.network_id
        }
        return repr(result)

    
class IntersectionGeocode(Geocode):
    def __init__(self, address=None, intersection=None):
        self.address = address
        self.intersection = intersection
        self.network_id = intersection.id
        self.xy = intersection.xy

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
            'network_id': self.network_id
        }
        return repr(result)
