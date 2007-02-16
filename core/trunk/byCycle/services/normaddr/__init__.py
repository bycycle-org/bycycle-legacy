"""$Id$

Address Normalization Service.

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

Accepts these types of addresses:
- Postal (e.g., 633 N Alberta, Portland, OR)
- Intersection (e.g., Alberta & Kerby)
- Point (e.g., x=-123, y=45)
- Node (i.e., node ID)
- Edge (i.e., number + edge ID).

"""
import re
from byCycle.util import gis
from byCycle.tripplanner.services import excs
from byCycle.tripplanner.model import mode, address, states, sttypes, compass


# RE to check to see if a string has at least one word char
re_word_plus = re.compile(r'\w+')

directions_ftoa = compass.directions_ftoa
directions_atof = compass.directions_atof
suffixes_ftoa = compass.suffixes_ftoa
suffixes_atof = compass.suffixes_atof
sttypes_ftoa = sttypes.street_types_ftoa
sttypes_atof = sttypes.street_types_atof
states_ftoa = states.states_ftoa
states_atof = states.states_atof


def get(region='', q='', **params):
    """Get a normalized address for the input address.

    @param string q Input address
    @param string|object region Region
    @return Address An address object with normalized attributes

    """
    # Fail early here if q is empty
    
    # First we should decide (guess) what type of address the input string is
    # supposed to be. Then we should fork and do different things accordingly
    # and return an Address object.

    # Check input
    errors = []

    if not region:
        errors.append('Please select a region')

    q = q.strip('"')
            
    if not q:
        errors.append('Please enter an address')

    if errors:
        raise excs.InputError(errors)    

    # Node?
    try:
        node_id = int(q)
    except ValueError:
        pass
    else:
        return address.NodeAddress(node_id)

    # Intersection?
    try:
        street1, street2 = getCrossStreets(q)
    except ValueError:
        pass
    else: 
        # parse streets and return IntersectionAddress
        street1, place1 = parse(street1, region)
        street2, place2 = parse(street2, region)
        return address.IntersectionAddress(street1, place1, street2, place2)
    
    # Edge?
    try:
        lAddr = q.split()        
        number = int(lAddr[0])
        edge_id = int(lAddr[1])
    except (IndexError, ValueError):
        pass
    else:
        return address.EdgeAddress(number, edge_id)
    
    # Postal Address?
    try:
        number, street = getNumberAndStreet(q)
    except ValueError:
        pass
    else:
        # parse street and return PostalAddress
        street, place = parse(street, region)
        return address.PostalAddress(number=number, street=street, place=place)

    # Point?
    try:
        point = gis.Point(q)
    except ValueError:
        pass
    else:
        return address.PointAddress(x=point.x, y=point.y)

    # Raise an exception if we get here: address is unnormalizeable
    raise ValueError('Could not parse address "%s" in region "%s"' %
                     (q, region))


def parse(sAddress, sOrOMode):
    """Parse input address string, referring to mode DB as necessary.

    The address *must* contain a street name
    The address must *not* contain a house number
    It *can* contain a city & state OR zip code OR both

    @param string sAddress A street & place with no number
           (e.g., Main St, Portland, OR)
    @param string|object sOrOMode Region to do lookup in if necessary
    @return object street, object place

    """
    if not isinstance(sOrOMode, mode.Mode):
        path = 'byCycle.tripplanner.model.%s'
        oMode = __import__(path % sOrOMode, globals(), locals(), ['']).Mode()
    else:
        oMode = sOrOMode

    sAddress = sAddress.replace(',', ' ')
    sAddress = sAddress.replace('.', '')
    tokens = sAddress.lower().split()
    name = []

    street = address.Street()
    place = address.Place()

    try:
        # If only one token, it must be the name
        if len(tokens) == 1:
            raise IndexError

        # -- Front to back
        
        # prefix
        prefix = tokens[0]
        if (prefix in directions_atof or prefix in directions_ftoa):
            if prefix in directions_ftoa:
                prefix = directions_ftoa[prefix]
            street.prefix = prefix
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
            place.zip_code = zip_code
            del tokens[-1]

        # state
        for i in (-1, -2, -3, -4):
            state_id = ' '.join(tokens[i:])
            if (state_id in states_atof or state_id in states_ftoa):
                if state_id in states_ftoa:
                    state = state_id
                    state_id = states_ftoa[state_id]
                else:
                    state = states_atof[state_id]
                place.state_id = state_id
                place.state = state
                del tokens[i:]
                break

        # city
        # TODO: make static list of cities for each region
        Q = 'SELECT id FROM %s_city WHERE city="%%s"' % oMode.region
        for i in (-1, -2, -3, -4):
            city = ' '.join(tokens[i:])
            if oMode.execute(Q % city):
                row = oMode.fetchRow()
                place.city_id = row[0]
                place.city = city
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
            street.suffix = suffix
            del tokens[-1]

        # street type
        sttype = tokens[-1]
        if (sttype in sttypes_atof or sttype in sttypes_ftoa): 
            if sttype in sttypes_ftoa:
                full_sttype = sttype
                sttype = sttypes_ftoa[sttype]
            street.sttype = sttype
            del tokens[-1]
    except IndexError:
        pass

    # Check name
    name = ' '.join(name + tokens)
    num_name = appendSuffixToNumberStreetName(name)
    try:
        # If a full street type was entered...
        full_sttype
    except NameError:
        name = num_name
    else:
        name_type = '%s %s' % (name, full_sttype)
        # ...and there is no street name in the DB with the name & type
        Q1 = 'SELECT id FROM %s_streetname WHERE name="%s" AND sttype="%s"' % \
             (oMode.region, num_name, street.sttype)
        # ...but there is one with the name with type appended to it
        Q2 = 'SELECT id FROM %s_streetname WHERE name = "%s"' % \
             (oMode.region, name_type)
        if not oMode.execute(Q1) and oMode.execute(Q2):
            # ...use the name with type appended as the name
            name = name_type
            # ...and assume there was no street type entered
            street.sttype = ''
    street.name = name

    return street, place


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
