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
from byCycle.tripplanner.model import mode, address, states, sttypes, compass
from byCycle.lib import gis

# RE to check see if a string has at least one word char
re_word_plus = re.compile(r'\w+')

directions_ftoa = compass.directions_ftoa
directions_atof = compass.directions_atof
suffixes_ftoa = compass.suffixes_ftoa
suffixes_atof = compass.suffixes_atof
sttypes_ftoa = sttypes.street_types_ftoa
sttypes_atof = sttypes.street_types_atof
states_ftoa = states.states_ftoa
states_atof = states.states_atof


def get(sAddr, sOrOMode):
    """Get a normalized address for the input address.

    @param string sAddr Input address
    @param string|object sOrOMode Region mode

    """
    # Fail early here if sAddr is empty
    
    # First we should decide (guess) what type of address the input string is
    # supposed to be. Then we should fork and do different things accordingly
    # and return an Address object.

    # Node?
    try:
        node_id = int(sAddr)
    except ValueError:
        pass
    else:
        return address.NodeAddress(node_id)

    # Intersection?
    try:
        street1, street2 = getCrossStreets(sAddr)
    except ValueError:
        pass
    else:
        # parse streets and return IntersectionAddress
        attrs1 = parse(street1, sOrOMode)
        attrs2 = parse(street2, sOrOMode)
        return address.IntersectionAddress()
    
    # Edge?
    try:
        lAddr = sAddr.split()        
        number = int(lAddr[0])
        edge_id = int(lAddr[1])
    except (IndexError, ValueError):
        pass
    else:
        return address.EdgeAddress(number, edge_id)
    
    # Address [postal]
    try:
        number, street = getNumberAndStreet(sAddr)
    except ValueError:
        pass
    else:
        # parse street and return PostalAddress
        attrs = parse(street, sOrOMode)
        return address.PostalAddress(number=number, **attrs)

    # Point?
    try:
        point = gis.Point(sAddr)
    except ValueError:
        pass
    else:
        return address.PointAddress(x=point.x, y=point.y)

    # Raise an exception if we get here: address is unnormalizeable


def parse(sAddress, sOrOMode):
    """Parse input address string, referring to mode DB as necessary.

    The address *must* contain a street name
    The address must *not* contain a house number
    It *can* contain a city & state OR zip code OR both

    @param string sAddress A street & place with no number
           (e.g., Main St, Portland, OR)
    @param string|object sOrOMode Region to do lookup in if necessary
    @return dictionary Address tokens containing keys for prefix, name, type,
            suffix, city, county, state, and zip code

    """
    if not isinstance(sOrOMode, mode.Mode):
        path = 'byCycle.tripplanner.model.%s'
        oMode = __import__(path % sOrOMode, globals(), locals(), ['']).Mode()
    else:
        oMode = sOrOMode

    attrs = dict(prefix='',
                 name='',
                 sttype='',
                 suffix='',
                 city='',
                 state='',
                 zip_code=None)
    sAddress = sAddress.replace(',', ' ')
    sAddress = sAddress.replace('.', '')
    tokens = sAddress.lower().split()
    name = []

    try:
        # If only one token, it must be the name
        if len(tokens) == 1:
            raise IndexError

        # -- Front to back
        
        # prefix
        prefix = tokens[0]
        if (prefix in directions_atof or prefix in directions_ftoa):
            if prefix in directions_ftoa:
                attrs['prefix'] = directions_ftoa[prefix]
            attrs['prefix'] = prefix
            del tokens[0]

        # name
        # Name must have at least one word
        name.append(tokens[0])
        del tokens[0]

        # -- Back to front

        # zip code
        zip_code = tokens[-1]
        try:
            int(zip_code)
        except ValueError:
            pass
        else:
            attrs['zip_code'] = zip_code
            del tokens[-1]

        # state
        for i in (-1, -2, -3, -4):
            state = ' '.join(tokens[i:])
            if (state in states_atof or state in states_ftoa):
                if state in states_ftoa:
                    state = states_ftoa[state]
                attrs['state'] = state
                del tokens[i:]
                break

        # city
        # TODO: make static list of cities for each region
        Q = 'SELECT id FROM %s_city WHERE city="%%s"' % oMode.region
        for i in (-1, -2, -3, -4):
            city = ' '.join(tokens[i:])
            if oMode.execute(Q % city):
                row = oMode.fetchRow()
                attrs['city'] = city
                del tokens[i:]
                break

        # suffix
        suffix = tokens[-1]
        if (suffix in directions_atof or suffix in suffixes_atof or
            suffix in directions_ftoa or suffix in suffixes_ftoa):
            if suffix in directions_ftoa:
                suffix = directions_ftoa[suffix]
            elif suffix in suffixes_ftoa:
                suffix = suffixes_ftoa[suffix]             
            attrs['suffix'] = suffix
            del tokens[-1]

        # street type
        sttype = tokens[-1]
        if (sttype in sttypes_atof or sttype in sttypes_ftoa): 
            if sttype in sttypes_ftoa:
                full_sttype = sttype
                sttype = sttypes_ftoa[sttype]
            attrs['sttype'] = sttype
            del tokens[-1]
    except IndexError:
        pass

    # Check name
    name = ' '.join(name + tokens)
    try:
        # If a full street type was entered...
        full_sttype
    except NameError:
        pass
    else:
        num_name = appendSuffixToNumberStreetName(name)
        name_type = '%s %s' % (name, full_sttype)
        # ...and there is no street name in the DB with the name & type
        Q1 = 'SELECT id FROM %s_streetname WHERE name="%s" AND type="%s"' % \
             (oMode.region, num_name, attrs['sttype'])
        # ...but there is one with the name with type appended to it
        Q2 = 'SELECT id FROM %s_streetname WHERE name = "%s"' % \
             (oMode.region, name_type)
        if not oMode.execute(Q1) and oMode.execute(Q2):
            # ...use the name with type appended as the name
            name = name_type
            # ...and assume there was no street type entered
            attrs['sttype'] = ''
    attrs['name'] = name

    return attrs


def appendSuffixToNumberStreetName(name):
    # Add suffix to number street (if needed), e.g. 10 => 10th
    try:
        int(name)
    except ValueError:
        pass
    else:
        last_char = name[-1]
        try:
            last_two_chars = name[-2:]
        except IndexError:
            last_two_chars = ''
        if   last_char == '1' and last_two_chars != '11': name += 'st'
        elif last_char == '2' and last_two_chars != '12': name += 'nd'
        elif last_char == '3' and last_two_chars != '13': name += 'rd'
        else:
            name += 'th'
    return name


def getCrossStreets(sAddr):
    """Try to extract two cross streets from the input address."""
    # Try splitting input addr on 'and', 'at', '&', '@', '+', '/', or '\'
    # 'and' or 'at' must have whitespace on both sides
    # All must have at least one word character on both sides
    sRe = r'\s+and\s+|\s+at\s+|\s*[&@\+/\\]\s*'
    oRe = re.compile(sRe, re.I)
    streets = re.split(oRe, sAddr)
    if (len(streets) > 1 and
        re.match(re_word_plus, streets[0]) and
        re.match(re_word_plus, streets[1])):
        return streets
    err = '"%s" could not be parsed as an intersection address' % sAddr
    raise ValueError(err)


def getNumberAndStreet(sAddr):
    """Try to extract a house number and street from the input address."""
    tokens = sAddr.split()
    if len(tokens) > 1:
        num = tokens[0]
        try:
            # Is num an int (house number)?
            num = int(num)
        except ValueError:
            # No.
            pass
        else:
            # num is an int; is street a string with at least one word char?
            street = ' '.join(tokens[1:])
            if re.match(re_word_plus, street):
                # Yes.
                return num, street 
    err = '"%s" could not be parsed as a postal address' % sAddr   
    raise ValueError(err)
