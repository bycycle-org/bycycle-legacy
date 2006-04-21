from byCycle.lib import gis
from byCycle.lib.util import joinAttrs




class AddressError(Exception): pass




class Address(object):
    pass




class PostalAddress(Address):
    def __init__(self, number=None, street=None, place=None):
        try:
            number = int(number)
        except:
            pass
        self.number = number
        if street is None:
            street = Street()
        self.street = street
        if place is None:
            place = Place()
        self.place = place


    def _getPrefix(self):
        return self.street.prefix
    def _setPrefix(self, new_prefix):
        self.street.prefix = new_prefix   
    prefix = property(_getPrefix, _setPrefix)

        
    def _getName(self):
        return self.street.name
    def _setName(self, new_name):
        self.street.name = new_name   
    name = property(_getName, _setName)

        
    def _getSttype(self):
        return self.street.sttype
    def _setSttype(self, new_sttype):
        self.street.sttype = new_sttype   
    sttype = property(_getSttype, _setSttype)

        
    def _getSuffix(self):
        return self.street.suffix
    def _setSuffix(self, new_suffix):
        self.street.suffix = new_suffix   
    suffix = property(_getSuffix, _setSuffix)


    def _getCityId(self):
        return self.place.city_id
    def _setCityId(self, new_city_id):
        self.place.city_id = new_city_id   
    city_id = property(_getCityId, _setCityId)

        
    def _getCity(self):
        return self.place.city
    def _setCity(self, new_city):
        self.place.city = new_city   
    city = property(_getCity, _setCity)

        
    def _getStateId(self):
        return self.place.state_id
    def _setStateId(self, new_state_id):
        self.place.state_id = new_state_id   
    state_id = property(_getStateId, _setStateId)

        
    def _getState(self):
        return self.place.state
    def _setState(self, new_state):
        self.place.state = new_state   
    state = property(_getState, _setState)


    def _getZipCode(self):
        return self.place.zip_code
    def _setZipCode(self, new_zip_code):
        self.place.zip_code = new_zip_code   
    zip_code = property(_getZipCode, _setZipCode)


    def __str__(self):
        result = joinAttrs([self.number, str(self.street)])
        result = joinAttrs([result, str(self.place)], '\n')
        return result


    def __repr__(self):
        return repr({'type': 'postal',
                     'number': self.number,
                     'street': self.street,
                     'place': self.place})
    


    
class EdgeAddress(PostalAddress):
    def __init__(self, number=None, edge_id=None):
        PostalAddress.__init__(self, number)
        self.edge_id = edge_id




class IntersectionAddress(Address):
    def __init__(self, street1=None, place1=None, street2=None, place2=None):
        if street1 is None:
            street1 = Street()
        if street2 is None:
            street2 = Street()

        self.street1, self.street2 = street1, street2

        if not place1 and not place2:
            place1 = Place()
            place2 = Place()
        elif not place1:
            place1 = place2
        elif not place2:
            place2 = place1

        self.place1, self.place2 = place1, place2


    def _getPrefix1(self):
        return self.street1.prefix
    def _setPrefix1(self, new_prefix1):
        self.street1.prefix = new_prefix1   
    prefix1 = property(_getPrefix1, _setPrefix1)

        
    def _getName1(self):
        return self.street1.name
    def _setName1(self, new_name1):
        self.street1.name = new_name1   
    name1 = property(_getName1, _setName1)

        
    def _getSttype1(self):
        return self.street1.sttype
    def _setSttype1(self, new_sttype1):
        self.street1.sttype = new_sttype1   
    sttype1 = property(_getSttype1, _setSttype1)

        
    def _getSuffix1(self):
        return self.street1.suffix
    def _setSuffix1(self, new_suffix1):
        self.street1.suffix = new_suffix1   
    suffix1 = property(_getSuffix1, _setSuffix1)


    def _getCityId1(self):
        return self.place1.city_id
    def _setCityId1(self, new_city_id1):
        self.place1.city_id = new_city_id1   
    city_id1 = property(_getCityId1, _setCityId1)

        
    def _getCity1(self):
        return self.place1.city
    def _setCity1(self, new_city1):
        self.place1.city = new_city1   
    city1 = property(_getCity1, _setCity1)

        
    def _getStateId1(self):
        return self.place1.state_id
    def _setStateId1(self, new_state_id1):
        self.place1.state_id = new_state_id1   
    state_id1 = property(_getStateId1, _setStateId1)

        
    def _getState1(self):
        return self.place1.state
    def _setState1(self, new_state1):
        self.place1.state = new_state1   
    state1 = property(_getState1, _setState1)


    def _getZipCode1(self):
        return self.place1.zip_code
    def _setZipCode1(self, new_zip_code1):
        self.place1.zip_code = new_zip_code1   
    zip_code1 = property(_getZipCode1, _setZipCode1)


    def _getPrefix2(self):
        return self.street2.prefix
    def _setPrefix2(self, new_prefix2):
        self.street2.prefix = new_prefix2   
    prefix2 = property(_getPrefix2, _setPrefix2)

        
    def _getName2(self):
        return self.street2.name
    def _setName2(self, new_name2):
        self.street2.name = new_name2   
    name2 = property(_getName2, _setName2)

        
    def _getSttype2(self):
        return self.street2.sttype
    def _setSttype2(self, new_sttype2):
        self.street2.sttype = new_sttype2   
    sttype2 = property(_getSttype2, _setSttype2)

        
    def _getSuffix2(self):
        return self.street2.suffix
    def _setSuffix2(self, new_suffix2):
        self.street2.suffix = new_suffix2   
    suffix2 = property(_getSuffix2, _setSuffix2)


    def _getCityId2(self):
        return self.place2.city_id
    def _setCityId2(self, new_city_id2):
        self.place2.city_id = new_city_id2   
    city_id2 = property(_getCityId2, _setCityId2)

        
    def _getCity2(self):
        return self.place2.city
    def _setCity2(self, new_city2):
        self.place2.city = new_city2   
    city2 = property(_getCity2, _setCity2)

        
    def _getStateId2(self):
        return self.place2.state_id
    def _setStateId2(self, new_state_id2):
        self.place2.state_id = new_state_id2   
    state_id2 = property(_getStateId2, _setStateId2)

        
    def _getState2(self):
        return self.place2.state
    def _setState2(self, new_state2):
        self.place2.state = new_state2   
    state2 = property(_getState2, _setState2)


    def _getZipCode2(self):
        return self.place2.zip_code
    def _setZipCode2(self, new_zip_code2):
        self.place2.zip_code = new_zip_code2   
    zip_code2 = property(_getZipCode2, _setZipCode2)

            
    def street(self):
        return joinAttrs((self.street1, self.street2), ' & ')
    street = property(street)


    def place(self):
        return str(self.place1)
    place = property(place)


    def __str__(self):
        return joinAttrs((self.street, self.place), '\n')
        
        
    def __repr__(self):
        return repr({'type': 'intersection',
                     'street1': self.street1,
                     'place1': self.place1,
                     'street2': self.street2,
                     'place2': self.place2})




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
    def __init__(self, prefix='', name='', sttype='', suffix=''):      
        self.prefix = prefix
        self.name = name
        self.sttype = sttype
        self.suffix = suffix


    def __str__(self):
        attrs = [self.prefix.upper(),
                 self._name(),
                 self.sttype.title(),
                 self.suffix.upper()]
        return joinAttrs(attrs)


    def __repr__(self):
        return repr({'prefix': str(self.prefix.upper()),
                     'name': str(self._name()),
                     'sttype': str(self.sttype.title()),
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
                 zip_code=''):
        self.city_id = city_id
        self.city = city
        self.state_id = state_id
        self.state = state
        self.zip_code = zip_code


    def __str__(self):
        result = joinAttrs((self.city.title(),
                            self.state_id.upper()),
                           ', ')
        return joinAttrs([result, str(self.zip_code)])


    def __repr__(self):
        return repr({'city': str(self.city.title()),
                     'city_id': str(self.city_id),
                     'state_id': str(self.state_id.upper()),
                     'state': str(self.state.title()),
                     'zip_code': str(self.zip_code)})

        
    def __eq__(self, other):
        if (self.city_id == other.city_id and
            self.city == other.city and
            self.state_id == other.state_id and
            self.state == other.state and
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
