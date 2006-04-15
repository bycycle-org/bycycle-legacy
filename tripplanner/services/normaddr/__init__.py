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


def parse(sStreet, sOrOMode):
    """Parse input street string, referring to mode DB only if necessary.

    Note: the 'street' is actually the street & place
    TODO: Change to something more appropriate

    A street should

    @param string sStreet A street & place
    @param string|object sOrOMode Region mode (DB) to do lookup in if necessary
    @return dictionary Address tokens containing keys for prefix, name, type,
            suffix, city, county, state, and zip code

    """
    if not isinstance(sOrOMode, mode.Mode):
        path = 'byCycle.tripplanner.model.%s'
        oMode = __import__(path % sOrOMode, globals(), locals(), ['']).Mode()
    else:
        oMode = sOrOMode

    name = []

    # TODO: Add these
    #no_prefixes = mode.NO_PREFIXES
    #no_suffixes = mode.NO_SUFFIXES

    # Remove punctuation chars here (and other extraneous chars too?)

    sStreet = sStreet.replace(',', '')
    sStreet = sStreet.replace('.', '')
    tokens = sStreet.lower().split()

    i = 0
    try:
        # prefix
        token = tokens[i]
        i+=1
        if token in directions_atof:
            prefix = token
            print 'prefix: %s' % prefix
        elif token in directions_ftoa:
            prefix = directions_ftoa[token]
        else:
            name.append(token)
            i-=1
        
        # street type
        token = tokens[i]
        i+=1
        if token in sttypes_atof: 
            sttype = token
            name.pop()
        elif token in sttypes_ftoa:
            sttype = sttypes_ftoa[token]
            name.pop()
        else:
            name.append(token)
            i-=1
            
        # suffix
        token = tokens[i]
        i+=1
        if (token in directions_atof or
            token in suffixes_atof):
            suffix = token
            name.pop()
        elif token in directions_ftoa:
            suffix = directions_ftoa[token]
            name.pop()
        elif token in suffixes_ftoa:
            suffix = suffixes_ftoa[token]                
            name.pop()
        else:
            name.append(token)
            i-=1

        # city
        # TODO: make static list of cities for each region
        token = tokens[i]
        i+=1
        Q = 'SELECT id FROM %s_city WHERE city="%s"' % \
            (oMode.region, token)
        oMode.execute(Q)
        row = oMode.fetchRow()
        if row:
            city = token
            name.pop()
        else:
            name.append(token)
            i-=1

        # state
        token = tokens[i]
        i+=1
        if token in states_atof:
            state = token
            name.pop()
        elif token in states_ftoa:
            state = states_ftoa[token]
            name.pop()
        else:
            name.append(token)
            i-=1

        # zip code
        token = tokens[i]
        try:
            int(token)
        except ValueError:
            name.append(token)
        else:
            name.pop()
            zip_code = token
    except IndexError:
        pass

    # name
    name += tokens
    name = ' '.join(name)

    # Add suffix to number street (if needed), e.g. 10 => 10th
    name = name
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
        name = name

    return locals()


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
