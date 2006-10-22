###########################################################################
# $Id$
# Created 2006-09-14.
#
# Domain objects.
#
# Copyright (C) 2006 Wyatt Baldwin, byCycle.org <wyatt@bycycle.org>.
# All rights reserved.
#
# For terms of use and warranty details, please see the LICENSE file included
# in the top level of this distribution. This software is provided AS IS with
# NO WARRANTY OF ANY KIND.


"""A collection of domain object definitions (AKA classes).

Some domain classes have been split out into other modules. This is usually
done when there are a set of related classes (such as the various address
classes) and exceptions.

`Node`
`Edge`
`StreetName`
`City`
`Place`
`Point`

"""
from sqlalchemy.sql import func, select

from byCycle.lib.util import joinAttrs
from byCycle.model.region import Region
from byCycle.model import regions


class Node(object):
    """Represents point features."""
    
    def __init__(self, id_, geom, edges=[]):
        self.id = id_
        self.geom = geom
        self.edges = edges

    def __str__(self):
        edges = '\n\n'.join([str(e) for e in self.edges])
        return 'NODE %s\n%s\n\n%s' % (self.id, self.geom, edges)


class Edge(object):
    """Represents line features."""

    def __init__(self, **attrs):
        self.__dict__.update(attrs)

    def getSideNumberIsOn(self, num):
        """Determine which side of the edge, "l" or "r", ``num`` is on."""
        # Determine odd side of edge, l or r, for convenience
        odd_side = ('l', 'r')[self.even_side == 'l']
        # Is ``num`` on the even or odd side of this edge?
        # FIXME: What if there's no address range on the side ``num`` is on?
        #        Right now, we return the odd side by default
        return (odd_side, self.even_side)[int(num) % 2 == 0]

    def getPlaceOnSideNumberIsOn(self, num):
        """Get `Place` on side ``num`` is on."""
        side = self.getSideNumberIsOn(num)
        if side == 'l':
            return self.place_l
        else:
            return self.place_r

    def _get_place_l(self):
        """Get `Place` on left side."""
        try:
            self.__place_l
        except AttributeError:
            self.__place_l = Place(
                city=self.city_l,
                state=self.state_l,
                zip_code=self.zip_code_l
            )
        return self.__place_l
    place_l = property(_get_place_l)

    def _get_place_r(self):
        """Get `Place` on right side."""
        try:
            self.__place_r
        except AttributeError:
            self.__place_r = Place(
                city=self.city_r,
                state=self.state_r,
                zip_code=self.zip_code_r
            )
        return self.__place_r
    place_r = property(_get_place_r)

    def __len__(self):
        """Get the length of this `Edge`, using cached value if available."""
        try:
            self._length
        except AttributeError:
            _c = self.c
            _f = func.length(_c.geom)
            select_ = select([_f.label('length')], _c.id == self.id)
            result = select_.execute()
            self._length = result.fetchone().length           
        return self._length

    def getPointAndLocationOfNumber(self, num):
        """
        
        ``num`` `int` -- A building number that should be in [addr_f, addr_t]
        
        return `Point`, `float` -- The coordinate that num is at within this
        `Edge`; the location, in range [0, 1], of ``num`` within this edge.
        
        """
        # Sanity check; num should always be an `int`
        num = int(num)
        
        # Determine location in [0, 1] of num along edge
        # Note: addr_f/t might be NULL
        if (not num) or (None in (self.addr_f, self.addr_t)):
            location = .5
        else:
            min_addr = min(self.addr_f, self.addr_t)
            max_addr = max(self.addr_f, self.addr_t)
            if min_addr == max_addr:
                location = .5
            else:
                edge_len = max_addr - min_addr
                dist_from_min_addr = num - min_addr
                location = dist_from_min_addr / edge_len

        _c = self.c

        # Function to get interpolated point
        _f = func.line_interpolate_point(_c.geom, location)
        # Function to transform point to lat/long
        _f = func.transform(_f, 4326)
        # Function to get WKT version of lat/long point
        _f = func.astext(_f)
        
        # Query DB and get WKT POINT
        select_ = select([_f.label('wkt_point')], _c.id == self.id)
        result = select_.execute()
        wkt_point = result.fetchone().wkt_point
        
        point = Point(point=wkt_point)
        return point, location
    
    def splitAtGeocode(self, geocode, node_id=-1, edge_f_id=-1, edge_t_id=-2):
        """Split this edge at ``geocode`` and return two new edges.

        ``geocode`` `Geocode` -- The geocode to split the edge at.
        
        See `splitAtLocation` for further details
        
        """        
        edge_f, edge_t = self.splitAtLocation(
            geocode.location, node_id, edge_f_id, edge_t_id
        )
        # address range
        num = geocode.address.number
        edge_f.addr_t = num
        edge_t.addr_f = num
        return edge_f, edge_t
        
    def splitAtNumber(self, num, node_id=-1, edge_f_id=-1, edge_t_id=-2):
        """Split this edge at ``num`` and return two new edges.

        ``num`` `int` -- The address number to split the edge at.
        
        See `splitAtLocation` for further details
        
        """
        point, location = self.getPointAndLocationOfNumber(num)
        return self.splitAtLocation(
            location, node_id, edge_f_id, edge_t_id
        )

    def splitAtLocation(self, location, node_id=-1, edge_f_id=-1, edge_t_id=-2):
        """Split this edge at ``location`` and return two new edges.

        The first edge is `node_f`=>``num``; the second is
        ``num``=>`node_t`. Distribute attributes of original edge to the two
        new edges.

        ``location`` `float` -- Location in range [0, 1] to split at
        ``node_id`` -- Node ID to assign the node at the split
        ``edge_f_id`` -- Edge ID to assign the `node_f`=>``num`` edge
        ``edge_t_id`` -- Edge ID to assign the ``num``=>`node_t` edge

        return `Edge`, `Edge` -- `node_f`=>``num``, ``num``=>`node_t` edges

        Recipe:
        - Determine location of num along edge; use .5 as default
        - Get XY at location
        - Get line geometry on either side of XY
        - Transfer geometry and attributes to two new edges
        - Return the  two new edges

        """
        edge_f, edge_t = self.clone(), self.clone()

        # TODO: Distribute other attributes proportionately
        #   - Geometry

        length = len(self)
        edge_f._length = length * location
        edge_t._length = length - len(edge_f)

        # fake segment IDs
        edge_f.id, edge_t.id = edge_f_id, edge_t_id
        # fake node ID
        edge_f.node_t_id, edge_t.node_f_id = node_id, node_id
        return edge_f, edge_t
    
    def clone(self):
        from copy import deepcopy
        return deepcopy(self)

    def __str__(self):
        stuff = [
            joinAttrs((
                'Address Range:',
                (self.addr_f or '[None]'),
                'to',
                (self.addr_t or '[None]')
                )),
            (self.street_name or '[No Street Name]'),
            joinAttrs(
                ('Cities: ',
                 (self.city_l or '[No Left Side City]'),
                 ', ',
                 (self.city_r or '[No Right Side City]')),
                join_string=''
            ),
            joinAttrs(
                ('States: ',
                 (self.state_l or '[No Left Side State]'),
                 ', ',
                 (self.state_r or '[No Right Side State]')),
                join_string=''
            ),
            joinAttrs(
                ('Zip Codes: ',
                 (self.zip_code_l or '[No Left Side Zip Code]'),
                 ', ',
                 (self.zip_code_r or '[No Right Side Zip Code]')),
                join_string=''
            ),
        ]
        return joinAttrs(stuff, join_string='\n')


class StreetName(object):
    def __init__(self, prefix=None, name=None, sttype=None, suffix=None):
        self.prefix = prefix
        self.name = name
        self.sttype = sttype
        self.suffix = suffix

    def __str__(self):
        attrs = (
            (self.prefix or '').upper(),
            self._name_for_str(),
            (self.sttype or '').title(),
            (self.suffix or '').upper()
        )
        return joinAttrs(attrs)

    def __repr__(self):
        return repr({
            'prefix': (self.prefix or '').upper(),
            'name': self._name_for_str(),
            'sttype': (self.sttype or '').title(),
            'suffix': (self.suffix or '').upper()
        })

    def _name_for_str(self):
        """Return lower case name if name starts with int, else title case."""
        name = self.name
        no_name = '[No Street Name]'
        try:
            int(name[0])
        except ValueError:
            name = name.title()
        except TypeError:
            # Street name not set (`None`)
            if name is None:
                name = name = no_name
            else:
                name = str(name)
        except IndexError:
            # Empty street name ('')
            name = no_name
        else:
            name = name.lower()
        return name

    def __nonzero__(self):
        """A `StreetName` must have at least a `name`."""
        return bool(self.name)


class City(object):
    """City.

    ``id`` `int` -- Unique ID
    ``city`` `string` -- City name
    
    """
    
    def __init__(self, id_=None, city=None):
        """See attributes list for description parameters."""
        self.id = id_
        self.city = city

    def __str__(self):
        if self.city:
            return self.city.title()
        else:
            return '[No City]'

    def __repr__(self):
        return repr({
            'id': self.id,
            'city': str(self)
        })
    
    def __nonzero__(self):
        """A `City` must have at least a `city` (i.e., a city name)."""
        return bool(self.city)


class State(object):
    """State.

    ``id`` `int` -- Unique ID
    ``state`` `string` -- State name
    
    """
   
    def __init__(self, id_=None, state=None):
        """See attributes list for description parameters."""
        self.id = id_
        self.state = state

    def __str__(self):
        if self.id:
            return self.id.upper()
        else:
            return '[No State]'

    def __repr__(self):
        return repr({
            'id': str(self),
            'state': str(self.state or '[No State]').title()
        })

    def __nonzero__(self):
        """A `State` can have either an id (two-letter abbrev.) or state."""
        return bool(self.id or self.state)


class Place(object):
    """City, state, and zip code.   
    
    ``city`` `City` -- City ID and city name
    ``state`` `State` -- State ID (two letter abbreviation) and state name
    ``zip_code`` `int`
    
    """
    
    def __init__(self, city=None, state=None, zip_code=None):
        """See attributes list for description parameters.
        
        Any or all of the parameters can be None.
        
        """
        if city is None:
            city = City()
        self.city = city
        if state is None:
            state = State()
        self.state = state
        self.zip_code = zip_code

    def _get_city_id(self):
        return self.city.id
    def _set_city_id(self, id_):
        self.city.id = id_
    city_id = property(_get_city_id, _set_city_id)

    def _get_city_name(self):
        return self.city.city
    def _set_city_name(self, name):
        self.city.city = name
    city_name = property(_get_city_name, _set_city_name)

    def _get_state_id(self):
        return self.state.id
    def _set_state_id(self, id_):
        self.state.id = id_
    state_id = property(_get_state_id, _set_state_id)

    def _get_state_name(self):
        return self.state.state
    def _set_state_name(self, name):
        self.state.state = name
    state_name = property(_get_state_name, _set_state_name)

    def __str__(self):
        city_state = joinAttrs([self.city, self.state], ', ')
        return joinAttrs([city_state, str(self.zip_code or '')])

    def __repr__(self):
        return repr({
            'city': self.city,
            'state': self.state,
            'zip_code': str(self.zip_code or '')
        })
    
    def __nonzero__(self):
        return bool(self.city or self.state or self.zip_code)


###########################################################################
class InitCoordinatesException(Exception):
    def __init__(self, msg):
        self.msg = msg


###########################################################################
class Point(object):
    """Simple point. Currently supports only X and Y (and not Z)."""

    #----------------------------------------------------------------------
    def __init__(self, point=None, x=None, y=None, z=None):
        """Coords can be given via ``point`` OR ``x`` AND ``y`` AND ``z``.

        ``point`` `string` | `list` | `tuple` | `object` | `dict`
            - A WKT geometry string (POINT(-123 45))
            - A sequence of floats (or string representations of floats)
            - A keyword args style string (x=-123, y=45)
            - An object with x, y, z attributes
            - A dict with x, y, and z keys
            - A string that will eval as an object, dict, tuple, or list

        ``x`` -- X coordinate
        ``y`` -- Y coordinate
        ``z`` -- Z coordinate

        Use ``x`` and ``y`` if both are given. Otherwise, get coordinates from
        ``point``. Currently, the Z coordinate is not supported.

        return `tuple` -- floats X and Y

        TODO: Support Z coordinate
        
        """
        self.x, self.y, self.z = self._initCoordinates(point, x, y, z)

    #----------------------------------------------------------------------
    def _initCoordinates(self, point, x, y, z):
        """Get x, y, and z coordinates.
        
        See __init__ for parameter details.
        
        ``point``
        ``x``
        ``y``
        ``z``
        
        return `tuple` -- X, Y, and Z coordinates. For now, Z is always None.
        
        raise ValueError
            - Coordinates cannot be parsed
            - Neither ``point`` nor both of ``x`` and ``y`` are given
        
        """
        if x is not None and y is not None:
            # ``x`` and ``y`` were passed; prefer them over ``point``.
            try:
                x, y = [float(v) for v in (x, y)]
            except (ValueError, TypeError):
                err = 'X and Y values must be floats. X: "%s", Y: "%s".'
                raise ValueError(err % (x, y))
            else:
                return x, y, None                
        elif point is not None:
            # ``point`` was passed and at least one of ``x`` and ``y`` wasn't
            # Try a bunch of different methods of parsing coordinates from
            # ``point``
            methods = (
                self._initCoordinatesFromObject,
                self._initCoordinatesFromDict,
                self._initCoordinatesFromEval,
                self._initCoordinatesFromKwargsString,
                self._initCoordinatesFromWKTString,
                self._initCoordinatesFromSequence,
            )
            for m in methods:
                try:
                    x, y = m(point)
                except InitCoordinatesException:
                    # Catch any "expected" exceptions--the _initCoordinates*
                    # methods catch various expected exceptions and raise
                    # this.
                    pass
                else:
                    try: 
                        x, y = [float(v) for v in (x, y)]
                    except (ValueError, TypeError):
                        pass
                    else:
                        return x, y, None
            raise ValueError(
                'Could not initialize coordinates from "%s".' % point
            )
        else:
            raise ValueError(
                'No arguments passed to initialize coordinates from. Pass '
                'either point OR x and y.'
            )
        
    #----------------------------------------------------------------------
    def _initCoordinatesFromSequence(self, s):
        try:
            return s[0], s[1]
        except IndexError:
            length = len(point)
            if length == 0:
                raise InitCoordinatesException('Missing x and y values.')
            elif length == 1:
                raise InitCoordinatesException(
                    'Missing y value (x: "%s").' % s[0]
                )
                        
    #----------------------------------------------------------------------
    def _initCoordinatesFromEval(self, s):
        try:
            eval_point = eval(s)
        except:
            raise InitCoordinatesException(
                '"%s" could not be evaled.' % str(s)
            )
        else:
            # Call recursively because we don't know what
            # point evaled as.
            x, y, z = self._initCoordinates(eval_point, None, None, None)
            return x, y

    #----------------------------------------------------------------------
    def _initCoordinatesFromWKTString(self, wkt):
        try:
            wkt = wkt.strip().upper()
            wkt = wkt.lstrip('POINT').strip()
            wkt = wkt.lstrip('(')
            wkt = wkt.rstrip(')')
            return wkt.split()
        except AttributeError:
            raise InitCoordinatesException(
                '"%s" does not appear to be a WKT point.' % str(wkt)
            )

    #----------------------------------------------------------------------
    def _initCoordinatesFromObject(self, obj):
        try:
            return obj.x, obj.y
        except AttributeError:
            raise InitCoordinatesException(
                '"%s" does not have both x and y attributes.' % str(obj)
            )
        
    #----------------------------------------------------------------------
    def _initCoordinatesFromDict(self, d):
        try:
            return d['x'], d['y']
        except KeyError:
            raise InitCoordinatesException(
                '"%s" does not contain both x and y keys.' % str(d)
            )
        except TypeError:
            raise InitCoordinatesException(
                '"%s" is not a dict.' % str(d)
            )            
    
    #----------------------------------------------------------------------
    def _initCoordinatesFromKwargsString(self, point):
        """A kwargs point is a str with x & y specified like keyword args.

        ``point`` `string` -- A string of this form: "x=-123, y=45"
            - x can be one of x, lng, lon, long, longitude
            - y can be one of y, lat, latitude
            - When x or y is not in the list, the first value will be used as
              the x value and the second as the y value
            - = can be one of [equal sign] or [colon]
            - , can be one of [comma] or [space]

        return `tuple` -- (float(x), float(y))

        raise `ValueError`

        """
        err = '"%s" is not a keyword-args style string.' % str(point)
        # Normalize point string
        try:
            point = ' '.join(point.strip().split())
        except AttributeError:
            raise InitCoordinatesException(err)
        puncs = ((' = ', '= ', ' ='), (' : ', ': ', ' :'), (' , ', ', ', ' ,'))
        norm_puncs = ('=', ':', ',')
        for ps, n in zip(puncs, norm_puncs):
            for p in ps:
                # Replace unnormalized puncuation, p, with normalized
                # punctuation, n.
                point = point.replace(p, n)

        # x and y will be either scalars or strings like "x=-123"
        try:
            x, y = point.split(',')
        except ValueError:
            x, y = point.split(' ')

        # Get x and y labels, if any
        try:
            x_label, x = x.split('=')
        except ValueError:
            try:
                x_label, x = x.split(':')
            except ValueError:
                # Assume positional, no label
                x_label = 'x'

        try:
            y_label, y = y.split('=')
        except ValueError:
            try:
                y_label, y = y.split(':')
            except ValueError:
                # Assume positional, no label
                y_label = 'y'

        x_labels = ('x', 'lng', 'lon', 'long', 'longitude')
        y_labels = ('y', 'lat', 'latitude')

        # Possibly swap X and Y if labels were given and
        if (x_label in y_labels) or (y_label in x_labels):
            x, y = y, x

        try:
            return x, y
        except NameError:
            raise InitCoordinatesException(err)           

    #----------------------------------------------------------------------
    def __str__(self):
        """Return a WKT string for this point."""
        return 'POINT (%.6f %.6f)' % (self.x, self.y)

    #----------------------------------------------------------------------
    def __repr__(self):
        return (
            "{'x': %.6f, 'y': %.6f, 'z': %.6f}" % 
            (self.x, self.y, self.z or 0.0)
        )
