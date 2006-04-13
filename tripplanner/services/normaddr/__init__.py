"""
Address Normalizer

Accepts these types of addresses:
- Postal
- Intersection
- Point
- Node (i.e., node ID)
- Edge (i.e., number + edge ID)
"""

import re
from byCycle.tripplanner.model import address, states, sttypes, compass


directions_ftoa = compass.directions_ftoa
directions_atof = compass.directions_atof
suffixes_ftoa = compass.suffixes_ftoa
suffixes_atof = compass.suffixes_atof
sttypes_ftoa = sttypes.street_types_ftoa
sttypes_atof = sttypes.street_types_atof
states_ftoa = states.states_ftoa
states_atof = states.states_atof


def get(addr, mode):
    """Get a normalized address for the input address."""

    # Fail early here if addr is empty

    # Remove punctuation chars here (and other extraneous chars too?)
    
    # First we should decide (guess) what type of address the input string is
    # supposed to be. Then we should fork and do different things accordingly
    # and return an Address object.

    # Node?
    try:
        node_id = int(addr)
    except ValueError:
        pass

    # Intersection?
    try:
        street1, street2 = getCrossStreets(addr)
    except ValueError:
        pass

    words = addr.split()
    
    # Edge?
    try:
        number = int(words[0])
        edge_id = int(words[1])
    except (IndexError, ValueError):
        pass

    # Address [postal]
    try:
        number = int(words[0])
        words[1]
    except (IndexError, ValueError):
        pass

    # Point?
    # XXX: Expensive; do last
    try:
        point = getPoint(addr)
    except ValueError:
        pass

    # Raise an exception if we get here: address is unnormalizeable



def _normalize(addr, mode):
    # This is the "meat" of this address normalizer
    name = []
    street = address.Street()
    place = address.Place()
    try:
        ## Front to back
 
        # prefix
        word = words[0]
        if word in directions_atof:
            street.prefix = word
        elif word in directions_ftoa:
            if len(words) == 1:
                raise IndexError
            else:
                street.prefix = directions_ftoa[word]
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
        if word in states_atof:
            place.state = word
        elif word in states_ftoa:
            place.state = states_ftoa[word]
        if place.state:
            del words[-1]

        # city
        # TODO: make static list of cities for each region
        word = words[-1]
        Q = 'SELECT id FROM %s_city WHERE city="%s"' % \
            (mode.region, word)
        mode.execute(Q)
        row = mode.fetchRow()
        if row:
            place.city_id = row[0]
            place.city = word
            del words[-1]

        # suffix
        word = words[-1]
        if word in directions_atof or \
               word in suffixes_atof:
            street.suffix = word
        elif word in directions_ftoa:
            street.suffix = directions_ftoa[word]
        elif word in suffixes_ftoa:
            street.suffix = suffixes_ftoa[word]                
        if street.suffix:
            del words[-1]

        # street type
        word = words[-1]
        if word in sttypes_atof: 
            street.type = word
        elif word in sttypes_ftoa:
            street.type = sttypes_ftoa[word]
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


def getIntersection(sAddr):
    and_re = re.compile(r'.+( and | at |[&@\+/\\]).+', re.I)
    if re.match(and_re, sAddr):
        return True
    else:
        return False
    

def what():
    for a in ands:
        streets = [sAddr for sAddr in sAddr.split(' %s ' % a)
                   if sAddr.strip()]
    if len(streets) >= 2:
        return street[0], street[1]
    err = '"%s" cannot be parsed as an intersection address' % sAddr
    raise ValueError(err)


def getPoint(sAddr):
    # String with form "x=-122, y=45"
    # x and y can be any string
    # = can be any char in the list on the next line
    # Note: this is the default version we expect from the front end
    for c in ('=', ':'):
        try:
            xy = sAddr.split(',')
            x = xy[0].split('%s' % c)[1]
            y = xy[1].split('%s' % c)[1]
            return gis.Point(x=float(x), y=float(y))
        except:
            pass

    # WKT string
    try:
        point = gis.importWktGeometry(sAddr)
        point.x
        point.y
        return point
    except:
        pass

    # gis.Point
    if isinstance(sAddr, gis.Point):
        return sAddr

    # X, Y object
    try:
        return gis.Point(x=float(sAddr.x), y=float(sAddr.y))
    except:
        pass

    # X, Y literal object
    try:
        return gis.Point(x=float(sAddr['x']), y=float(sAddr['y']))
    except:
        pass

    # String with form "(-122, 45)"
    try:
        obj = eval(sAddr)
        if len(obj) < 2:
            raise ValueError
        if not isinstance(obj, tuple):
            raise
        return gis.Point(x=float(obj[0]), y=float(obj[1]))
    except:
        pass

    # String with form "-122, 45"
    # , can be any char in the list on the next line
    for c in (',', ' '):
        try:
            xy = sAddr.split(c)
            return gis.Point(x=float(xy[0]), y=float(xy[1]))
        except:
            pass
        
    err = '"%s" cannot be parsed as a point address' % sAddr
    raise ValueError(err)


    

if __name__ == '__main__':
    import unittest
    #import byCycle.tripplanner.services import normaddr
    from byCycle.tripplanner.model import portlandor


    class TestIsIntersection(unittest.TestCase):
        def testCall(self):
            isIntersection('')

        def testAnd(self):
            is_i = isIntersection('A and B')
            self.assertTrue(is_i)
            is_i = isIntersection('A And B')
            self.assertTrue(is_i)
            is_i = isIntersection('A aNd B')
            self.assertTrue(is_i)
            is_i = isIntersection('A anD B')
            self.assertTrue(is_i)
            is_i = isIntersection('A AND B')
            self.assertTrue(is_i)

        def testAt(self):
            is_i = isIntersection('A at B')
            self.assertTrue(is_i)
            is_i = isIntersection('A At B')
            self.assertTrue(is_i)
            is_i = isIntersection('A aT B')
            self.assertTrue(is_i)
            is_i = isIntersection('A AT B')
            self.assertTrue(is_i)

        def testAtSymbol(self):
            is_i = isIntersection('A @ B')
            self.assertTrue(is_i)
            is_i = isIntersection('A @B')
            self.assertTrue(is_i)            
            is_i = isIntersection('A@ B')
            self.assertTrue(is_i)
            is_i = isIntersection('A@B')
            self.assertTrue(is_i)

        def testForwardSlash(self):
            is_i = isIntersection('A / B')
            self.assertTrue(is_i)
            is_i = isIntersection('A /B')
            self.assertTrue(is_i)            
            is_i = isIntersection('A/ B')
            self.assertTrue(is_i)            
            is_i = isIntersection('A/B')
            self.assertTrue(is_i)
            
        def testBackSlash(self):
            is_i = isIntersection(r'A \ B')
            self.assertTrue(is_i)
            is_i = isIntersection(r'A \B')
            self.assertTrue(is_i)            
            is_i = isIntersection(r'A\ B')
            self.assertTrue(is_i)            
            is_i = isIntersection(r'A\B')
            self.assertTrue(is_i)
            
        def testPlus(self):
            is_i = isIntersection('A + B')
            self.assertTrue(is_i)
            is_i = isIntersection('A +B')
            self.assertTrue(is_i)            
            is_i = isIntersection('A+ B')
            self.assertTrue(is_i)            
            is_i = isIntersection('A+B')
            self.assertTrue(is_i)

        def testMissingInternalSpace(self):
            is_i = isIntersection('A andB')
            self.assertFalse(is_i)            
            is_i = isIntersection('Aat B')
            self.assertFalse(is_i)

        def testMissingFromOrTo(self):
            is_i = isIntersection('and B')
            self.assertFalse(is_i)            
            is_i = isIntersection('A at')
            self.assertFalse(is_i)
            is_i = isIntersection(' and B')
            self.assertFalse(is_i)            
            is_i = isIntersection('A at ')
            self.assertFalse(is_i)

        def testMissingFromAndTo(self):
            is_i = isIntersection('and')
            self.assertFalse(is_i)                
            is_i = isIntersection(' and')
            self.assertFalse(is_i)
            is_i = isIntersection('and ')
            self.assertFalse(is_i)                
            is_i = isIntersection(' and ')
            self.assertFalse(is_i)                
            


    class TestNormAddr:
        def testCreatePortlandORMode(self):
            mode = portlandor.Mode()

        def testUsePortlandORMode(self):
            mode = portlandor.Mode()
            mode.execute('show columns from portlandor_layer_street')
        
        def testPortlandORAddressAddress(self): 
            mode = portlandor.Mode()
            inaddr = '4807 SE Kelly St, Portland, OR 97206'
            self.assert_(isinstance(get(inaddr, mode),
                                    address.AddressAddress))

        def testPortlandORIntersectionAddress(self):
            inaddr = 'SE Kelly St & SE 49th Ave, Portland, OR 97206'
            mode = portlandor.Mode()
            self.assert_(isinstance(get(inaddr, mode),
                                    address.IntersectionAddress))

        def testPortlandORPointAddress(self):
            inaddr = 'POINT(-123.120000 45.000000)'
            mode = portlandor.Mode()
            self.assert_(isinstance(get(inaddr, mode), address.PointAddress))
            self.assert_(isinstance(get(inaddr, mode),
                                    address.IntersectionAddress))

        def testPortlandORNodeAddress(self):
            inaddr = '4'
            mode = portlandor.Mode()
            self.assert_(isinstance(get(inaddr, mode),
                                    address.IntersectionAddress))

        def testPortlandOREdgeAddress(self):
            mode = portlandor.Mode()
            Q = 'SELECT id FROM portlandor_layer_street ' \
                'WHERE addr_f <= 4807 AND addr_t >= 4807 AND ' \
                'streetname_id IN ' \
                '(SELECT id from portlandor_streetname ' \
                ' WHERE prefix = "se" AND name = "kelly" AND type = "st")'
            mode.execute(Q)
            edge_id = mode.fetchRow()[0]
            inaddr = '4807 %s' % edge_id
            self.assert_(isinstance(get(inaddr, mode), address.AddressAddress))

            
    unittest.main()
    
