from byCycle.tripplanner.model import address, states, sttypes, compass


directions_ftoa = compass.directions_ftoa
directions_atof = compass.directions_atof
suffixes_ftoa = compass.suffixes_ftoa
suffixes_atof = compass.suffixes_atof
street_types_ftoa = sttypes.street_types_ftoa
street_types_atof = sttypes.street_types_atof
states_ftoa = states.states_ftoa
states_atof = states.states_atof

@staticmethod
def getCrossStreets(sAddr): 
    ands = ('&', 'and', 'AND', 'at', 'AT', '@')
    for a in ands:
        streets = [sAddr for sAddr in sAddr.split(' %s ' % a)
                   if sAddr.strip()]
    if len(streets) >= 2:
        return streets
    err = 'invalid address for IntersectionAddress: %s' % sAddr
    raise ValueError(err)


@staticmethod
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

    err = 'Invalid address for PointAddress: %s' % sAddr
    raise ValueError(err)


def get(addr, mode):
    if isinstance(addr, basestring):
        words = addr.split() 
    elif isinstance(addr, list):
        words = addr
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
        # TODO: make static list of cities for each region
        word = words[-1]
        Q = 'SELECT id FROM %s_city WHERE city="%s"' % \
            (self.mode.region, word)
        self.mode.execute(Q)
        row = self.mode.fetchRow()
        if row:
            place.city_id = row[0]
            place.city = word
            del words[-1]

        # suffix
        word = words[-1]
        if word in self.directions_atof or \
               word in self.suffixes_atof:
            street.suffix = word
        elif word in self.directions_ftoa:
            street.suffix = self.directions_ftoa[word]
        elif word in self.suffixes_ftoa:
            street.suffix = self.suffixes_ftoa[word]                
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
    
