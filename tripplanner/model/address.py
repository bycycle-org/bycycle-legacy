# Characters not allowed in an address
disallowed_chars_re = r"[^a-zA-Z0-9 '-]"
# Characters allowed only once in an address
allowed_once_chars = "'-"

import states
import sttypes
import compass


## "Static" "Methods"

def joinAttrs(attrs, join_string=' '):
    return join_string.join([str(a) for a in attrs if a])


## Exceptions

class AddressError(Exception): pass
class AddressNotFoundError(AddressError): pass


class Address(object):
    def __init__(self, inaddr, mode):
        type_inaddr = type(inaddr)
        if type_inaddr not in (type(''), type(u''), type({})):
            err = 'Must supply address string or attributes dict'
            raise AddressError(err)

        inaddr = inaddr.strip().lower()
        for c in (',', '.'): inaddr = inaddr.replace(c, '')
        self.inaddr = inaddr
        
        self.mode = mode
        self.directions_ftoa = compass.directions_ftoa
        self.directions_atof = compass.directions_atof
        self.street_types_ftoa = sttypes.street_types_ftoa
        self.street_types_atof = sttypes.street_types_atof
        self.states_ftoa = states.states_ftoa
        self.states_atof = states.states_atof


    def _initStreetAndPlace(self, inaddr):
        if isinstance(inaddr, basestring): words = inaddr.split() 
        elif isinstance(inaddr, list): words = inaddr
        name = []
        street = Street()
        place = Place()
        try:
            ## Front to back

            # prefix
            word = words[0]
            if word in self.directions_atof:
                street.prefix = word
            elif word in self.directions_ftoa:
                if len(words) == 1:
                    raise IndexError
                else:
                    street.prefix = self.directions_ftoa[word]
            if street.prefix:
                del words[0]

            # name
            name.append(words[0])
            del words[0]

            ## Back to front

            # zip code
            word = words[-1]
            try:
                int(word)
            except ValueError:
                pass
            else:
                place.zip = word
                del words[-1]

            # state
            word = words[-1]
            if word in self.states_atof:
                place.state = word
            elif word in self.states_ftoa:
                place.state = self.states_ftoa[word]
            if place.state:
                del words[-1]

            # city
            word = words[-1]
            Q = 'SELECT id FROM city WHERE city="%s"' % (word)
            self.mode.execute(Q)
            row = self.mode.fetchRow()
            if row:
                place.city_id = row[0]
                place.city = word
                del words[-1]

            # suffix
            word = words[-1]
            if word in self.directions_atof: street.suffix = word
            elif word in self.directions_ftoa:
                street.suffix = self.directions_ftoa[word]
            if street.suffix:
                del words[-1]

            # street type
            word = words[-1]
            if word in self.street_types_atof: 
                street.type = word
            elif word in self.street_types_ftoa:
                street.type = self.street_types_ftoa[word]
            if street.type:
                del words[-1]

        except IndexError:
            pass

        # name
        name += words
        street.name = ' '.join(name)

        # Add suffix to number street (if needed), e.g. 10 => 10th
        name = street.name
        try: int(name)
        except ValueError: pass
        else:
            last_char = name[-1]
            try: last_two_chars = name[-2:]
            except IndexError: last_two_chars = ''
            if   last_char == '1' and last_two_chars != '11': name += 'st'
            elif last_char == '2' and last_two_chars != '12': name += 'nd'
            elif last_char == '3' and last_two_chars != '13': name += 'rd'
            else: name += 'th'
            street.name = name
        
        return street, place


class AddressAddress(Address):
    def __init__(self, inaddr, mode, **kwargs):
        Address.__init__(self, inaddr, mode, **kwargs)
        words = self.inaddr.split()
        try: self.number = int(words[0])
        except: self.number = 0
        else: words = words[1:]
        self.street, self.place = self._initStreetAndPlace(words)
        
    def __str__(self):        
        result = joinAttrs([self.number, str(self.street)])
        result = joinAttrs([result, str(self.place)], '\n')
        return result
    

class IntersectionAddress(Address):
    def __init__(self, inaddr, mode, **kwargs):
        Address.__init__(self, inaddr, mode, **kwargs)
        if inaddr:
            streets = self.getCrossStreets(self.inaddr)
            self.street1, self.place1 = self._initStreetAndPlace(streets[0])
            self.street2, self.place2 = self._initStreetAndPlace(streets[1])
        else: 
            self.street1, self.place1 = Street(), Place()
            self.street2, self.place2 = Street(), Place()
        if not self.place1: self.place1 = self.place2
        if not self.place2: self.place2 = self.place1

    @staticmethod
    def getCrossStreets(inaddr): 
        ands = ('&', 'and', 'AND', 'at', 'AT')
        for a in ands:
            streets = [addr for addr in inaddr.split(' %s ' % a)
                       if addr.strip()]
            if len(streets) >= 2: return streets
        err = 'invalid address for IntersectionAddress: %s' % inaddr
        raise ValueError(err)

    def street(self):
        return joinAttrs((self.street1, self.street2), ' & ')
    street = property(street)

    def place(self):
        if self.place1 == self.place2:
            return str(self.place1)
        else:
            joinAttrs((self.place1, self.place2), ' & ')
    place = property(place)

    def __str__(self):
        return joinAttrs((self.street, self.place), '\n')


class PointAddress(IntersectionAddress):
    def __init__(self, inaddr, mode, **kwargs):
        IntersectionAddress.__init__(self, '', mode, **kwargs)
        self.x, self.y = self.getXY(inaddr)

    @staticmethod
    def getXY(inaddr):
        try:
            # (-122, 45) 
            obj = eval(inaddr)
            if len(obj) < 2: raise
            if type(obj) != type((1,2)): raise
            x, y = obj[0], obj[1]
        except:
            try:
                # x=-122, y=45
                xy = inaddr.split(',')
                x = xy[0].split('=')[1]
                y = xy[1].split('=')[1]
            except:
                err = 'invalid address for PointAddress: %s' % inaddr
                raise ValueError(err)
        return float(x), float(y)

    def __str__(self):
        try: return IntersectionAddress.__str__(self)
        except AttributeError: return str(('%.6f' % self.x, '%.6f' % self.y))

    
class Street(object):
    def __init__(self, prefix='', name='', stype='', suffix=''):
        self.prefix = prefix
        self.name = name
        self.type = stype
        self.suffix = suffix

    def getIds(self, mode):
        """Get all the street name IDs for this Street.

        Return a dict of {street name IDs => street names}

        """
        cur = mode.cursor
        Q = 'SELECT %s FROM %s WHERE %s'
        C = ('id', 'prefix', 'name', 'type', 'suffix')
        A = (self.prefix, self.name, self.type, self.suffix)
        where = ['%s="%s"' % (c, a.lower()) for (c, a) in zip(C[1:], A) if a]
        where = ' AND '.join(where)
        if where: 
            cols_str = ', '.join(C)
            cur.execute(Q % (cols_str, mode.tables['streetnames'], where))
            stnameids = {}
            for row in cur.fetchall(): stnameids[row[0]] = joinAttrs(row[1:])
            if stnameids: return stnameids
        err = 'Could not find street %s' % joinAttrs(A)
        raise AddressNotFoundError(err)

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
        try: int(name[0])
        except ValueError: name = name.title()
        except IndexError: name = '?'
        else: name = name.lower()
        return name


class Place(object):
    def __init__(self,
                 city_id=0, city='',
                 county_id=0, county='',
                 state_id='', state='',
                 zipcode=0):
        self.city_id = city_id
        self.city = city
        self.county_id = county_id
        self.county = county
        self.state_id = state_id
        self.state = state
        self.zip = zipcode

    def __str__(self):
        result = joinAttrs((self.city.title(),
                            self.county.title(),
                            self.state_id.upper()),
                           ', ')
        return joinAttrs([result, str(self.zip)])

    def __repr__(self):
        return repr({'city': str(self.city.title()),
                     'county': str(self.county.title()),
                     'state_id': str(self.state_id.upper()),
                     'zipcode': str(self.zip)})
        
    def __eq__(self, other):
        if \
           self.city_id == other.city_id and \
           self.city == other.city and \
           self.county_id == other.county_id and \
           self.county == other.county and \
           self.state_id == other.state_id and \
           self.state == other.state and \
           self.zip == other.zip:
            return True
        else:
            return False

    def __ne__(self, other):
        if self.__eq__: return False
        else: return True

    def __nonzero__(self):
        if \
           self.city_id or self.city or \
           self.county_id or self.county or \
           self.state_id or self.state or \
           self.zip:
            return True
        else:
            return False       
        
           
if __name__ == "__main__":
    from metro import data
    mode = data.Mode()
    
    a = AddressAddress('4408 se stark st portland oregon 97215', mode)
    print a
    print a.number
    print a.street, a.place
    print
    
    b = IntersectionAddress('44th and stark oregon', mode)
    print b
    print b.street1, b.place1
    print b.street2, b.place2
    print

    c = PointAddress('(-122.684927, 45.564424)', mode)
    print c
    
