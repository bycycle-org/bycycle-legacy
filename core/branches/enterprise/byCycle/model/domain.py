###############################################################################
# $Id$
# Created 2006-09-14.
#
# Entity classes.
#
# Copyright (C) 2006 Wyatt Baldwin, byCycle.org <wyatt@bycycle.org>.
# All rights reserved.
#
# For terms of use and warranty details, please see the LICENSE file included
# in the top level of this distribution. This software is provided AS IS with
# NO WARRANTY OF ANY KIND.
###############################################################################
"""Entity classes."""
import os
import marshal
import math

from sqlalchemy.sql import func, select

from elixir import Entity
from elixir import options_defaults, using_options, using_table_options
from elixir import has_field
from elixir import belongs_to, has_one, has_many, has_and_belongs_to_many
from elixir import Unicode, Integer, String, CHAR, Integer, Numeric, Float

import simplejson

from cartography import geometry
from cartography.proj import SpatialReference

from byCycle import model_path
from byCycle.util import joinAttrs
from byCycle.model.data.sqltypes import POINT, LINESTRING

from byCycle.model.portlandor import data as portlandor_data


options_defaults['shortnames'] = True

cascade_args = dict(
    constraint_kwargs={'ondelete': 'cascade'},
    cascade='all, delete-orphan'
)


def __to_builtin(self):
    return dict([(col.key, getattr(self, col.key)) for col in self.c])
Entity.to_builtin = __to_builtin
def __to_json(self):
    return simplejson.dumps(self.to_builtin())
Entity.to_json = __to_json
def __repr(self):
    return repr(self.to_builtin())
Entity.__repr__ = __repr


# These "constants" are used when creating the adjacency matrix for a region
# The number of digits to save when encoding a float as an int
float_exp = 6
# Multiplier to create int-encoded float
float_encode = 10 ** float_exp
# Multiplier to get original float value back
float_decode = 10 ** -float_exp

def encodeFloat(f):
    """Encode the float ``f`` as an integer."""
    return int(math.floor(f * float_encode))

def decodeFloat(i):
    """Decode the int ``i`` back to its original float value."""
    return i * float_decode


class Region(Entity):
    has_field('title', String)
    has_field('slug', String)
    has_field('srid', Integer)
    has_field('units', String)
    has_field('earth_circumference', Integer)
    has_many('edges', of_kind='Edge')
    has_many('nodes', of_kind='Node')
    has_many('edge_attrs', of_kind='EdgeAttr', order_by='id')
    has_many('geocodes', of_kind='Geocode')
    has_many('routes', of_kind='Route')
    has_many('ads', of_kind='Ad')
    has_many('places', of_kind='Place')
    has_and_belongs_to_many('street_names', of_kind='StreetName',
                            cascade='all, delete-orphan')
    has_and_belongs_to_many('cities', of_kind='City',
                            cascade='all, delete-orphan')
    has_and_belongs_to_many('states', of_kind='State',
                            cascade='all, delete-orphan')

    @property
    def data_path(self):
        return os.path.join(model_path, self.slug, 'data')

    @property
    def matrix_path(self):
        return os.path.join(self.data_path, 'matrix.pyc')

    @property
    def edge_attrs_index(self):
        """Create an index of adjacency matrix street attributes.

        In the ``matrix``, there is an (ordered) of edge attributes for each
        edge. ``edge_attrs_index`` gives us a way to access those attributes
        by name while keeping the size of the matrix smaller. We require that
        edges for all regions have at least a length, street name ID, and
        from-node ID.

        """
        edge_attrs = ['length', 'streetname_id', 'node_f_id']
        edge_attrs += [a.name for a in self.edge_attrs]
        edge_attrs_index = {}
        for i, attr in enumerate(edge_attrs):
            edge_attrs_index[attr] = i
        return edge_attrs_index

    def _get_adjacency_matrix(self):
        """Return matrix. Prefer 1) existing 2) disk 3) newly created."""
        matrix = getattr(self, '_matrix', None)
        if matrix is None:
            try:
                loadfile = open(self.matrix_path, 'rb')
            except IOError:
                matrix = self.createAdjacencyMatrix()
            else:
                try:
                    matrix = marshal.load(loadfile)
                except (EOFError, ValueError, TypeError):
                    matrix = self.createAdjacencyMatrix()
                loadfile.close()
            self._matrix = matrix
        return matrix

    def _set_adjacency_matrix(self, matrix):
        self._matrix = matrix
        dumpfile = open(self.matrix_path, 'wb')
        marshal.dump(matrix, dumpfile)
        dumpfile.close()

    matrix = G = property(_get_adjacency_matrix, _set_adjacency_matrix)

    def createAdjacencyMatrix(self):
        """Create the adjacency matrix for this DB's region.

        Build a matrix suitable for use with the route service. The structure
        of the matrix is defined by/in the Dijkstar package.

        return
            Adjacency matrix for this region:
                {nodes: {}, edges: {}}
                    nodes: {v: {v: e, v: e, ...}, v: {v: e, v: e, ...}, ...}
                    edges: {e: (attrs), e: (attrs), ...}

        """
        from byCycle.util.meter import Meter, Timer

        timer = Timer()

        def took():
            print 'Took %s seconds.' % timer.stop()

        num_nodes = Node.count_by(region=self)

        timer.start()
        edge_id_name = '%s_edge_id' % self.slug
        print 'Fetching edge attributes...'
        c = Edge.c
        cols = [c.id, c.node_f_id, c.node_t_id, c.one_way, c.street_name_id,
                c[edge_id_name]]
        select_ = select(cols)
        select_.append_whereclause((c.region_id == self.id))
        rows = select_.execute()
        bases = dict([(r[edge_id_name], r) for r in rows])
        took()

        timer.start()
        print 'Fetching regional edge attributes...'
        region_rows = self._getEdgeRowsForMatrix()
        num_edges = region_rows.rowcount
        took()

        timer.start()
        print 'Total number of edges in region: %s' % len(bases)
        print 'Number of filtered edges: %s' % num_edges
        print 'Number of nodes in region: %s' % num_nodes
        print 'Creating adjacency matrix...'
        matrix = {'nodes': {}, 'edges': {}}
        nodes = matrix['nodes']
        edges = matrix['edges']
        meter = Meter(num_items=num_edges, start_now=True)
        meter_i = 1
        for row in region_rows:
            adjustments = self._adjustEdgeRowForMatrix(row)
            ix = row.id
            base = bases[ix]
            node_f_id, node_t_id = base.node_f_id, base.node_t_id
            one_way = base.one_way
            # 0: no travel in either direction
            # 1: travel from => to only
            # 2: travel to => from only
            # 3: travel in both directions
            ft = one_way & 1
            tf = one_way & 2
            entry = [encodeFloat(row.geom.length()), base.street_name_id,
                     base.node_f_id]
            entry += [row[a.name] for a in self.edge_attrs]
            for k in adjustments:
                entry[self.edge_attrs_index[k]] = adjustments[k]
            edges[ix] = tuple(entry)
            if ft:
                if not node_f_id in nodes:
                    nodes[node_f_id] = {}
                nodes[node_f_id][node_t_id] = ix
            if tf:
                if not node_t_id in nodes:
                    nodes[node_t_id] = {}
                nodes[node_t_id][node_f_id] = ix
            meter.update(meter_i)
            meter_i += 1
        rows.close()
        region_rows.close()
        print
        took()

        timer.start()
        print 'Saving adjacency matrix...'
        self.matrix = matrix
        took()

    @property
    def edge_entity(self):
        return self._get_entity('edge')

    @property
    def node_entity(self):
        return self._get_entity('node')

    def _get_entity(self, name):
        entity = getattr(self, '_%s_entity' % name, None)
        if entity is None:
            entity_name = '%s_%s' % (self.slug, name)
            for name, obj in globals().items():
                if hasattr(obj, '__class__') and name.lower() == entity_name:
                    entity = obj
                    break
            setattr(self, '_%s_entity' % name, entity)
        return entity

    def _getEdgeRowsForMatrix(self):
        return self.edge_entity._getRowsForMatrix()

    def _adjustEdgeRowForMatrix(self, row):
        return self.edge_entity._adjustRowForMatrix(row)

    def __str__(self):
        return '%s: %s' % (self.slug, self.title)


class EdgeAttr(Entity):
    using_options(tablename='edge_attrs')
    has_field('name', String)
    belongs_to('region', of_kind='Region', **cascade_args)
    def __repr__(self):
        return str(self.name)


class Ad(Entity):
    has_field('title', String)
    has_field('href', String)
    has_field('text', String)
    belongs_to('region', of_kind='Region', **cascade_args)
    def __str__(self):
        return ' '.join([self.title, self.href, self.text])


class Service(Entity):
    has_field('title', String)
    belongs_to('region', of_kind='Region', inverse='geocodes', **cascade_args)


class Geocode(Entity):
    has_field('title', String)
    belongs_to('region', of_kind='Region', inverse='geocodes', **cascade_args)


class Route(Entity):
    has_field('title', String)
    belongs_to('region', of_kind='Region', **cascade_args)


class Node(Entity):
    belongs_to('region', of_kind='Region', **cascade_args)
    belongs_to('portlandor_node', of_kind='PortlandOR_Node', **cascade_args)
    has_many('edges_f', of_kind='Edge', inverse='node_f')
    has_many('edges_t', of_kind='Edge', inverse='node_t')

    @property
    def edges(self):
        return list(self.edges_f) + list(self.edges_t)


class PortlandOR_Node(Entity):
    has_field('geom', POINT(portlandor_data.SRID))
    has_one('base', of_kind='Node')
    

class Edge(Entity):
    has_field('addr_f', Integer)
    has_field('addr_t', Integer)
    has_field('even_side', CHAR(1)),
    has_field('one_way', Integer)
    belongs_to('node_f', of_kind='Node', **cascade_args)
    belongs_to('node_t', of_kind='Node', **cascade_args)
    belongs_to('street_name', of_kind='StreetName', **cascade_args)
    belongs_to('place_l', of_kind='Place', **cascade_args)
    belongs_to('place_r', of_kind='Place', **cascade_args)
    belongs_to('region', of_kind='Region', **cascade_args)
    belongs_to('portlandor_edge', of_kind='PortlandOR_Edge', **cascade_args)

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
            self._length = self.geom.length()
        return self._length

    def getPointAndLocationOfNumber(self, num):
        """

        ``num`` `int` -- A building number that should be in [addr_f, addr_t]

        return `Point`, `float` -- The coordinate that ``num`` is at within
        this `Edge`; the location, in range [0, 1], of ``num`` within this
        edge.

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
                location = float(dist_from_min_addr) / edge_len

        _c = self.c

        # Function to get interpolated point
        _f = func.line_interpolate_point(_c.geom, location)
        # Function to get WKB version of lat/long point
        _f = func.asbinary(_f)

        # Query DB and get WKB POINT
        select_ = select([_f.label('wkb_point')], _c.id == self.id)
        result = select_.execute()
        wkb_point = result.fetchone().wkb_point

        point = geometry.Geometry.fromWKB(wkb_point)
        return point, location

    def splitAtGeocode(self, geocode, node_id=-1, edge_f_id=-1, edge_t_id=-2):
        """Split this edge at ``geocode`` and return two new edges.

        ``geocode`` `Geocode` -- The geocode to split the edge at.

        See `splitAtLocation` for further details

        """
        edge_f, edge_t = self.splitAtLocation(
            geocode.xy, geocode.location, node_id, edge_f_id, edge_t_id
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
            point, location, node_id, edge_f_id, edge_t_id
        )

    def splitAtLocation(self, point, location,
                        node_id=-1, edge_f_id=-1, edge_t_id=-2):
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

        TODO: Distribute ``geom`` attributes proportionately

        """
        num_points = self.geom.numPoints()
        points = [self.geom.pointN(i) for i in range(num_points)]
        N = int(num_points * location) or 1
        if N == num_points:
            N -= 1
        edge_f_points = points[:N] + [point]
        edge_t_points = [point] + points[N:]
        srs = self.geom.srs
        edge_f_geom = geometry.LineString(points=edge_f_points, srs=srs)
        edge_t_geom = geometry.LineString(points=edge_t_points, srs=srs)

        edge_f = Edge(id=edge_f_id,
                      node_f_id=self.node_f_id, node_t_id=node_id,
                      street_name=self.street_name,
                      geom=edge_f_geom)
        edge_t = Edge(id=edge_t_id,
                      node_f_id=node_id, node_t_id=self.node_t_id,
                      street_name=self.street_name,
                      geom=edge_t_geom)

        shared_node = Node(node_id, self.geom.pointN(N))
        edge_f.node_f = Node(self.node_f_id, self.geom.startPoint())
        edge_f.node_t = shared_node
        edge_t.node_f = shared_node
        edge_t.node_t = Node(self.node_t_id, self.geom.endPoint())

        return edge_f, edge_t

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

    def to_builtin(self):
        attrs = [col.key for col in self.c]
        vals = [getattr(self, a) for a in attrs]
        simple = dict(zip(attrs, vals))
        #linestring = self.geom.copy()
        #srs = SpatialReference(epsg=4326)
        #linestring.transform(src_proj=str(self.geom.srs), dst_proj=str(srs))
        #points = []
        #for i in range(linestring.numPoints()):
            #points.append(linestring.pointN(i))
        #simple['geom'] = [{'x': p.x, 'y': p.y} for p in points]
        return simple


class PortlandOR_Edge(Entity):
    has_field('geom', LINESTRING(2913))
    has_field('localid', Numeric(11, 2) )
    has_field('code', Integer)
    has_field('bikemode', CHAR(1))  # enum('','p','t','b','l','m','h','c','x')
    has_field('up_frac', Float)
    has_field('abs_slope', Float)
    has_field('cpd', Integer)
    has_field('sscode', Integer)
    has_one('base', of_kind='Edge', inverse='portlandor_edge')

    @classmethod
    def _getRowsForMatrix(cls):
        code = cls.c.code
        region_rows = cls.table.select((
            ((code >= 1200) & (code < 1600)) |
            ((code >= 3200) & (code < 3300))
        )).execute()
        return region_rows

    @classmethod
    def _adjustRowForMatrix(cls, row):
        adjustments = {
            'abs_slope': encodeFloat(row.abs_slope),
            'up_frac': encodeFloat(row.up_frac),
        }
        return adjustments


class StreetName(Entity):
    has_field('prefix', String(2))
    has_field('name', String)
    has_field('sttype', String(4))
    has_field('suffix', String(2))
    has_and_belongs_to_many('regions', of_kind='Region',
                            cascade='all, delete-orphan')

    def __str__(self):
        attrs = (
            (self.prefix or '').upper(),
            self._name_for_str(),
            (self.sttype or '').title(),
            (self.suffix or '').upper()
        )
        return joinAttrs(attrs)

    def to_builtin(self):
        return {
            'prefix': (self.prefix or '').upper(),
            'name': self._name_for_str(),
            'sttype': (self.sttype or '').title(),
            'suffix': (self.suffix or '').upper()
        }

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

    def __eq__(self, other):
        self_attrs = (self.prefix, self.name, self.sttype, self.suffix)
        try:
            other_attrs = (other.prefix, other.name, other.sttype, other.suffix)
        except AttributeError:
            return False
        return (self_attrs == other_attrs)

    def almostEqual(self, other):
        self_attrs = (self.name, self.sttype)
        try:
            other_attrs = (other.name, other.sttype)
        except AttributeError:
            return False
        return (self_attrs == other_attrs)


class City(Entity):
    has_field('city', String)
    has_and_belongs_to_many('regions', of_kind='Region',
                            cascade='all, delete-orphan')

    def __str__(self):
        if self.city:
            return self.city.title()
        else:
            return '[No City]'

    def to_builtin(self):
        return {
            'id': self.id,
            'city': str(self)
        }

    def __nonzero__(self):
        return bool(self.city)


class State(Entity):
    has_field('code', CHAR(2))  # Two-letter state code
    has_field('state', String)
    has_and_belongs_to_many('regions', of_kind='Region',
                            cascade='all, delete-orphan')

    def __str__(self):
        if self.code:
            return self.code.upper()
        else:
            return '[No State]'

    def to_builtin(self):
        return {
            'id': self.id,
            'code': str(self),
            'state': str(self.state or '[No State]').title()
        }

    def __nonzero__(self):
        return bool(self.code or self.state)



class Place(Entity):
    has_field('zip_code', Integer)
    belongs_to('city', of_kind='City', **cascade_args)
    belongs_to('state', of_kind='State', **cascade_args)
    belongs_to('region', of_kind='Region', **cascade_args)

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

    def _get_state_code(self):
        return self.state.code
    def _set_state_code(self, code):
        self.state.code = code
    state_code = property(_get_state_code, _set_state_code)

    def _get_state_name(self):
        return self.state.state
    def _set_state_name(self, name):
        self.state.state = name
    state_name = property(_get_state_name, _set_state_name)

    def __str__(self):
        city_state = joinAttrs([self.city, self.state], ', ')
        return joinAttrs([city_state, str(self.zip_code or '')])

    def to_builtin(self):
        return {
            'city': self.city.to_builtin(),
            'state': self.state.to_builtin(),
            'zip_code': str(self.zip_code or '')
        }

    def __nonzero__(self):
        return bool(self.city or self.state or self.zip_code)


class InitCoordinatesException(Exception):
    def __init__(self, msg):
        self.msg = msg


class Point(object):
    """Simple point. Currently supports only X and Y (and not Z)."""

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
                'Could not initialize coordinates from "%s".' % str(point)
            )
        else:
            raise ValueError(
                'No arguments passed to initialize coordinates from. Pass '
                'either point OR x and y.'
            )

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

    def _initCoordinatesFromObject(self, obj):
        try:
            return obj.x, obj.y
        except AttributeError:
            raise InitCoordinatesException(
                '"%s" does not have both x and y attributes.' % str(obj)
            )

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

    def __str__(self):
        """Return a WKT string for this point."""
        return 'POINT (%.6f %.6f)' % (self.x, self.y)

    def __repr__(self):
        return (
            "{'x': %.6f, 'y': %.6f, 'z': %.6f}" %
            (self.x, self.y, self.z or 0.0)
        )
