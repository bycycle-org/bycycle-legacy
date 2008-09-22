###############################################################################
# $Id$
# Created 2006-09-14.
#
# Public (i.e., shared) entity classes.
#
# Copyright (C) 2006, 2007 Wyatt Baldwin, byCycle.org <wyatt@bycycle.org>.
# All rights reserved.
#
# For terms of use and warranty details, please see the LICENSE file included
# in the top level of this distribution. This software is provided AS IS with
# NO WARRANTY OF ANY KIND.
###############################################################################
"""Entities that are shared by all regions; they live in the public SCHEMA."""
import os, marshal

from sqlalchemy import Column, ForeignKey, func, select
from sqlalchemy.orm import relation
from sqlalchemy.types import Integer, String, CHAR, Float

from byCycle import model_path
from byCycle.util import joinAttrs
from byCycle.model import db
from byCycle.model.entities import DeclarativeBase
from byCycle.model.entities.util import cascade_arg, encodeFloat

__all__ = [
    'Region', 'EdgeAttr', 'Service', 'Geocode', 'Route', 'StreetName',
    'City', 'State', 'Place']


# A place to keep references to adjacency matrices so they don't need to be
# continually read from disk
matrix_registry = {}


class Region(DeclarativeBase):
    __tablename__ = 'regions'

    member_name = 'region'
    collection_name = 'regions'
    member_title = 'Region'
    collection_title = 'Regions'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    slug = Column(String)
    srid = Column(Integer)
    units = Column(String)
    earth_circumference = Column(Float)
    block_length = Column(Float)
    jog_length = Column(Float)

    edge_attrs = relation(
        'EdgeAttr', backref='region', order_by='EdgeAttr.id',
        cascade=cascade_arg)

    required_edge_attrs = [
        'length',
        'street_name_id',
        'node_f_id',
        'code',
        'bikemode'
    ]

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
        edges for all regions have at least a length, street name ID,
        from-node ID, street classification (AKA code), and bike mode.

        """
        edge_attrs = self.required_edge_attrs[:]
        # Add the region-specific edge attributes used for routing
        edge_attrs += [a.name for a in self.edge_attrs]
        edge_attrs_index = {}
        for i, attr in enumerate(edge_attrs):
            edge_attrs_index[attr] = i
        return edge_attrs_index

    def _get_adjacency_matrix(self):
        """Return matrix. Prefer 1) existing 2) disk 3) newly created."""
        matrix = matrix_registry.get(self.slug, None)
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
            matrix_registry[self.slug] = matrix
        return matrix

    def _set_adjacency_matrix(self, matrix):
        matrix_registry[self.slug] = matrix
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

        timer.start()
        print 'Fetching edge attributes...'
        c = self.module.Edge.c
        cols = [c.id, c.node_f_id, c.node_t_id, c.one_way, c.street_name_id,
                c.geom, c.code, c.bikemode]
        cols += [a.name for a in self.edge_attrs]
        rows = select(cols).execute()
        num_edges = rows.rowcount
        took()

        timer.start()
        print 'Total number of edges in region: %s' % num_edges
        print 'Creating adjacency matrix...'
        matrix = {'nodes': {}, 'edges': {}}
        nodes = matrix['nodes']
        edges = matrix['edges']
        meter = Meter(num_items=num_edges, start_now=True)
        meter_i = 1
        for row in rows:
            adjustments = self._adjustEdgeRowForMatrix(row)

            ix = row.id
            node_f_id = row.node_f_id
            node_t_id = row.node_t_id
            one_way = row.one_way

            entry = [encodeFloat(row.geom.length())]
            entry += [row[attr] for attr in self.required_edge_attrs[1:]]
            entry += [row[a.name] for a in self.edge_attrs]
            for k in adjustments:
                entry[self.edge_attrs_index[k]] = adjustments[k]
            edges[ix] = tuple(entry)

            # One way values:
            # 0: no travel in either direction
            # 1: travel from => to only
            # 2: travel to => from only
            # 3: travel in both directions

            if one_way & 1:
                nodes.setdefault(node_f_id, {})[node_t_id] = ix
            if one_way & 2:
                nodes.setdefault(node_t_id, {})[node_f_id] = ix

            meter.update(meter_i)
            meter_i += 1
        rows.close()
        print
        took()

        timer.start()
        print 'Saving adjacency matrix...'
        self.matrix = matrix
        took()

    @property
    def module(self):
        module = getattr(self, '_module', None)
        if module is None:
            path = 'byCycle.model.%s' % self.slug
            exec 'from %s import Node, Edge' % path
            class M(object): pass
            module = M()
            module.Node, module.Edge = Node, Edge
            #module = __import__(path, locals(), globals(), [''])
            self._module = module
        return module

    def _get_entity(self, name):
        entity = getattr(self, '_%s_entity' % name, None)
        if entity is None:
            entity = getattr(self.module, name)
            setattr(self, '_%s_entity' % name, entity)
        return entity

    def _adjustEdgeRowForMatrix(self, row):
        return self.module.Edge._adjustRowForMatrix(row)

    def __str__(self):
        return '%s: %s' % (self.slug, self.title)


class EdgeAttr(DeclarativeBase):
    __tablename__ = 'edge_attrs'
    id = Column(Integer, primary_key=True)
    region_id = Column(Integer, ForeignKey('regions.id'))
    name = Column(String)
    def __repr__(self):
        return str(self.name)


class Service(DeclarativeBase):
    __tablename__ = 'services'
    id = Column(Integer, primary_key=True)
    region_id = Column(Integer, ForeignKey('regions.id'))


class Geocode(DeclarativeBase):
    __tablename__ = 'geocodes'
    id = Column(Integer, primary_key=True)
    region_id = Column(Integer, ForeignKey('regions.id'))


class Route(DeclarativeBase):
    __tablename__ = 'routes'
    id = Column(Integer, primary_key=True)
    region_id = Column(Integer, ForeignKey('regions.id'))


class StreetName(DeclarativeBase):
    __tablename__ = 'street_names'

    id = Column(Integer, primary_key=True)
    prefix = Column(String(2))
    name = Column(String)
    sttype = Column(String(4))
    suffix = Column(String(2))

    def __str__(self):
        attrs = (
            (self.prefix or '').upper(),
            self._name_for_str(),
            (self.sttype or '').title(),
            (self.suffix or '').upper()
        )
        return joinAttrs(attrs)

    def to_simple_object(self):
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


class City(DeclarativeBase):
    __tablename__ = 'cities'

    id = Column(Integer, primary_key=True)
    city = Column(String)

    def __str__(self):
        if self.city:
            return self.city.title()
        else:
            return '[No City]'

    def to_simple_object(self):
        return {
            'id': self.id,
            'city': str(self)
        }

    def __nonzero__(self):
        return bool(self.city)


class State(DeclarativeBase):
    __tablename__ = 'states'

    id = Column(Integer, primary_key=True)
    code = Column(CHAR(2))  # Two-letter state code
    state = Column(String)

    def __str__(self):
        if self.code:
            return self.code.upper()
        else:
            return '[No State]'

    def to_simple_object(self):
        return {
            'id': self.id,
            'code': str(self),
            'state': str(self.state or '[No State]').title()
        }

    def __nonzero__(self):
        return bool(self.code or self.state)



class Place(DeclarativeBase):
    __tablename__ = 'places'

    id = Column(Integer, primary_key=True)
    zip_code = Column(Integer)
    city_id = Column(Integer, ForeignKey('cities.id'))
    state_id = Column(Integer, ForeignKey('states.id'))

    city = relation('City', cascade=cascade_arg)
    state = relation('State', cascade=cascade_arg)

    def _get_city_name(self):
        return (self.city.city if self.city is not None else None)
    def _set_city_name(self, name):
        if self.city is None:
            self.city = City()
        self.city.city = name
    city_name = property(_get_city_name, _set_city_name)

    def _get_state_code(self):
        return (self.state.code if self.state is not None else None)
    def _set_state_code(self, code):
        if self.state is None:
            self.state = State()
        self.state.code = code
    state_code = property(_get_state_code, _set_state_code)

    def _get_state_name(self):
        return (self.state.state if self.state is not None else None)
    def _set_state_name(self, name):
        if self.state is None:
            self.state = State()
        self.state.state = name
    state_name = property(_get_state_name, _set_state_name)

    def __str__(self):
        city_state = joinAttrs([self.city, self.state], ', ')
        return joinAttrs([city_state, str(self.zip_code or '')])

    def to_simple_object(self):
        return {
            'city': (self.city.to_simple_object() if self.city is not None else None),
            'state': (self.state.to_simple_object() if self.state is not None else None),
            'zip_code': str(self.zip_code or None)
        }

    def __nonzero__(self):
        return bool(self.city or self.state or (self.zip_code is not None))
