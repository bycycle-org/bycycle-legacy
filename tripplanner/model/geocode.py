# Geocode classes


from byCycle.lib import gis

    
class Geocode(object):
    def __str__(self):
        return str(self.address)

    
class PostalGeocode(Geocode):
    def __init__(self, address=None, segment=None, xy=None):
        self.address = address
        self.segment = segment
        self.xy = xy
        
    def __repr__(self):
        result = {'type': 'address',
                  'number': self.address.number,
                  'street': self.address.street,
                  'place': self.address.place,
                  'address': str(self.address),
                  'x': '%.6f' % self.xy.x,
                  'y': '%.6f' % self.xy.y,
                  'e': self.segment.id}
        return repr(result)

    
class IntersectionGeocode(Geocode):
    def __init__(self, address=None, intersection=None):
        self.address = address
        self.intersection = intersection
        self.xy = intersection.lon_lat

    def __repr__(self):
        result = {'type': 'intersection',
                  'street1': self.address.street1,
                  'street2': self.address.street2,
                  'place1': self.address.place1,
                  'place2': self.address.place2,
                  'address': str(self.address),                  
                  'x': '%.6f' % self.xy.x,
                  'y': '%.6f' % self.xy.y,
                  'v': self.intersection.id}
        return repr(result)
