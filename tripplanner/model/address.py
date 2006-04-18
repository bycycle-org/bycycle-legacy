from byCycle.lib import gis
from byCycle.lib.util import joinAttrs




class AddressError(Exception): pass




class Address(object):
    def __init__(self, **attrs):
        # Assign keyword arguments to self
        for attr in self.attrs:
            # Use keyword arg if passed; else use default
            val = attrs.get(attr, self.attrs[attr])
            try:
                words = val.split()
            except AttributeError:
                pass
            else:
                val = ' '.join(words)
            setattr(self, attr, val)

    
    def __repr__(self):
        for attr in self.attrs:
            self.attrs[attr] = self.__dict__[attr]
        return repr(self.attrs)




class PostalAddress(Address):
    attr_order = ('number',
                  'prefix', 'name', 'sttype', 'suffix',
                  'city_id' ,'city', 'state_id', 'state', 'zip_code')
    
    attrs = dict(number=None,
                 prefix='', name='', sttype='', suffix='',
                 city_id=None, city='', state_id='', state='', zip_code=None)

    
    def __init__(self, **attrs):
        Address.__init__(self, **attrs)
        
        try:
            self.number = int(self.number)
        except:
            pass
        try:
            self.zip_code = int(self.zip_code)
        except:
            pass
        
        self.street = Street(self.prefix, self.name, self.sttype, self.suffix)
        self.place = Place(self.city_id, self.city, self.state_id, self.state,
                           self.zip_code)


    def __str__(self):
        result = joinAttrs([self.number, str(self.street)])
        result = joinAttrs([result, str(self.place)], ', ')
        return result



    
class EdgeAddress(PostalAddress):
    def __init__(self, number=None, edge_id=None):
        PostalAddress.__init__(self, number=number)
        self.edge_id = edge_id


    def __str__(self):
        return PostalAddress.__str__(self)




class IntersectionAddress(Address):
    attr_order = ('prefix1', 'name1', 'sttype1', 'suffix1',
                  'city_id1', 'city1', 'state_id1', 'state1', 'zip_code1',
                  'prefix2', 'name2', 'sttype2', 'suffix2',
                  'city_id2', 'city2', 'state_id2', 'state2', 'zip_code2')
    
    attrs = dict(prefix1='', name1='', sttype1='', suffix1='',
                 city_id1=None, city1='', state_id1='', state1='',
                 zip_code1=None,
                 prefix2='', name2='', sttype2='', suffix2='',
                 city_id2=None, city2='', state_id2='', state2='',
                 zip_code2=None)

    
    def __init__(self, **attrs):
        Address.__init__(self, **attrs)

        try:
            self.zip_code1 = int(self.zip_code1)
        except:
            pass
        try:
            self.zip_code2 = int(self.zip_code2)
        except:
            pass

        self.street1 = Street(self.prefix1, self.name1, self.sttype1,
                              self.suffix1)
        self.street2 = Street(self.prefix2, self.name2, self.sttype2,
                              self.suffix2)
        
        place1 = Place(self.city_id1, self.city1, self.state_id1, self.state1,
                       self.zip_code1)
        place2 = Place(self.city_id2, self.city2, self.state_id2, self.state2,
                       self.zip_code2)
        if place2 and not place1:
            place1 = place2
        if not place2:
            place2 = place1
        self.place1, self.place2 = place1, place2

            
    def street(self):
        return joinAttrs((self.street1, self.street2), ' & ')
    street = property(street)


    def place(self):
        return str(self.place1)
    place = property(place)


    def __str__(self):
        return joinAttrs((self.street, self.place), ', ')
        
        



class PointAddress(IntersectionAddress):
    def __init__(self, x=None, y=None):
        IntersectionAddress.__init__(self)
        self.point = gis.Point(x=x, y=y)
        self.x = self.point.x
        self.y = self.point.y


    def __str__(self):
        s = IntersectionAddress.__str__(self)
        if s == '? & ?':
            s = str(self.point)
        return s




class NodeAddress(IntersectionAddress):
    def __init__(self, node_id=None):
        IntersectionAddress.__init__(self)
        self.node_id = node_id


    def __str__(self):
        s = IntersectionAddress.__str__(self)
        if s == '? & ?':
            s = str(self.node_id)
        return s


        
    
class Street(object):
    def __init__(self, prefix='', name='', stype='', suffix=''):
        self.prefix = prefix
        self.name = name
        self.type = stype
        self.suffix = suffix


    def __str__(self):
        attrs = [self.prefix.upper(),
                 self._name(),
                 self.type.title(),
                 self.suffix.upper()]
        return joinAttrs(attrs)


    def __repr__(self):
        return repr({'prefix': str(self.prefix.upper()),
                     'name': str(self._name()),
                     'type': str(self.type.title()),
                     'suffix': str(self.suffix.upper())})        


    def _name(self):
        """If name is like 3rd return lower name, else return title name."""
        name = self.name
        try:
            int(name[0])
        except ValueError:
            name = name.title()
        except IndexError:
            name = '?'
        else:
            name = name.lower()
        return name




class Place(object):
    def __init__(self, city_id=None, city='', state_id='', state='',
                 zip_code=None):
        self.city_id = city_id
        self.city = city
        self.state_id = state_id
        self.state = state
        self.zip_code = zip_code


    def __str__(self):
        result = joinAttrs((self.city.title(),
                            self.state_id.upper()),
                           ', ')
        return joinAttrs([result, str(self.zip_code or '')])


    def __repr__(self):
        return repr({'city': str(self.city.title()),
                     'city_id': str(self.city_id),
                     'state_id': str(self.state_id.upper()),
                     'zip_code': str(self.zip_code or '')})

        
    def __eq__(self, other):
        if (self.city == other.city_id and
            self.state == other.state_id and
            self.zip_code == other.zip_code):
            return True
        else:
            return False


    def __ne__(self, other):
        if self == other:
            return False
        else:
            return True


    def __nonzero__(self):
        if (self.city_id or self.city or self.state_id or self.state or
            self.zip_code):
            return True
        else:
            return False       
