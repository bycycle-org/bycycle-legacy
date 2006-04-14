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


def get(sAddr, mode):
    """Get a normalized address for the input address."""

    # Fail early here if sAddr is empty

    # Remove punctuation chars here (and other extraneous chars too?)
    
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
        pass
    
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
        pass

    # Point?
    # XXX: Expensive; do last
    try:
        point = gis.Point(sAddr)
    except ValueError:
        pass
    else:
        return address.PointAddress(x=point.x, y=point.y)

    # Raise an exception if we get here: address is unnormalizeable



def _normalize(sAddr, mode):
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
    words = sAddr.split()
    if len(words) > 1:
        num = words[0]
        try:
            # Is num an int (house number)?
            num = int(num)
        except ValueError:
            # No.
            pass
        else:
            # num is an int; is street a string with at least one word char?
            street = ' '.join(words[1:])
            if re.match(re_word_plus, street):
                # Yes.
                return num, street 
    err = '"%s" could not be parsed as a postal address' % sAddr   
    raise ValueError(err)
