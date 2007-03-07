################################################################################
# $Id: region.py 331 2006-11-15 01:34:36Z bycycle $
# Created 2006-09-11
#
# Regions base.
#
# Copyright (C) 2006 Wyatt Baldwin, byCycle.org <wyatt@bycycle.org>.
# All rights reserved.
#
# For terms of use and warranty details, please see the LICENSE file included
# in the top level of this distribution. This software is provided AS IS with
# NO WARRANTY OF ANY KIND.
################################################################################
"""Provides the `Region` base class."""
import os
import marshal
import math
from sqlalchemy.sql import select
from sqlalchemy.orm import mapper, relation
from byCycle.model import db
from byCycle.model.domain import *


# The number of digits to save when encoding a float as an int
float_exp = 6
# Multiplier to create int-encoded float
float_encode = 10 ** float_exp
# Multiplier to get original float value back
float_decode = 10 ** -float_exp


# TODO: Get this from the DB somehow
regions = {
    'portlandor': {
        'SRID': 2913,
        'title': 'Portland, OR',
        'units': 'feet',
        'earth_circumference': 131484672
    },
    
    'milwaukeewi': {
        'SRID': 2913,
        'title': 'Milwaukee, WI',
        'units': 'feet',
        'earth_circumference': 131484672
    },
    
    'pittsburghpa': {
        'SRID': 2913,
        'title': 'Milwaukee, WI',
        'units': 'feet',
        'earth_circumference': 131484672
    }    
}


class Mappers(object):
    def __getitem__(self, key):
        """Allow access to mappers using dict notation."""
        try:
            return self.__dict__[key]
        except KeyError:
            raise KeyError('Unknown mapper: %s' % (key))


class Region(object):
    """Base class for regions."""

    def __init__(self, key):
        """

        ``key`` is a unique identifier for the region, suitable for use as a
        dictionary/hash/javascript key. It should be the same as the region's
        package name.
        
        TODO: Get the geometry/spatial attrs from the DB (SRID, units, etc)

        """
        self.key = key
        attrs = regions[key]
        self.title = attrs['title']
        self.SRID = attrs['SRID']
        self.units = attrs['units']
        self.earth_circumference = attrs['earth_circumference']

        # This region's adjacency matrix
        self.G = None

        # Create an index of adjacency matrix street attributes. In the matrix,
        # there is an ordered sequence of edge attributes for each street.
        # This index gives us a way to access the attributes by name while
        # keeping the size of the matrix smaller. We require that streets for
        # all regions have at least a length attribute.
        self.edge_attrs = ['length'] + self.edge_attrs
        self.edge_attrs_index = {}
        for i, attr in enumerate(self.edge_attrs):
            self.edge_attrs_index[attr] = i

        self.float_encode = float_encode
        self.float_decode = float_decode
        
        # Set up path to data files for this region
        self.data_path = os.path.join(db.model_path, key, 'data')
        self.matrix_path = os.path.join(self.data_path, 'matrix.pyc')

    @property
    def tables(self):
        try: 
            self._tables
        except AttributeError:
            imp_path = 'byCycle.model.%s.data.tables' % self.key
            tables_mod = __import__(imp_path, globals(), locals(), [''])
            self._tables = tables_mod.Tables(
                self.key, self.SRID, db.metadata
            )
        return self._tables

    @property
    def mappers(self):
        """Initialize database-table <==> domain-object mappers."""
        try:
            self._mappers
        except AttributeError:
            mappers = Mappers()
            tables = self.tables
            layer_nodes = tables.layer_nodes
            street_names = tables.street_names
            cities = tables.cities
            states = tables.states
            layer_edges = tables.layer_edges
            edges_c = layer_edges.c
            nodes_c = layer_nodes.c
            mappers.layer_nodes = mapper(
                Node,
                layer_nodes,
                properties={
                    'edges': relation(
                        Edge,
                        primaryjoin=(
                            (nodes_c.id == edges_c.node_f_id) |
                            (nodes_c.id == edges_c.node_t_id)
                        ),
                    )
                },
            )
            mappers.street_names = mapper(
                StreetName,
                street_names,
            )
            mappers.cities = mapper(
                City,
                cities,
            )
            mappers.states = mapper(
                State,
                states,
            )
            mappers.layer_edges = mapper(
                Edge,
                layer_edges,
                properties={
                    'node_f': relation(
                        Node,
                        primaryjoin=edges_c.node_f_id == nodes_c.id,
                        backref='edges'
                        ),
                    'node_t': relation(
                        Node,
                        primaryjoin=edges_c.node_t_id == nodes_c.id,
                        backref='edges',
                        ),
                    'street_name': relation(
                        StreetName,
                        ),
                    'city_l': relation(
                        City,
                        primaryjoin=edges_c.city_l_id == cities.c.id,
                        ),
                    'city_r': relation(
                        City,
                        primaryjoin=edges_c.city_r_id == cities.c.id,
                        ),
                    'state_l': relation(
                        State,
                        primaryjoin=edges_c.state_l_id == states.c.id,
                        ),
                    'state_r': relation(
                        State,
                        primaryjoin=edges_c.state_r_id == states.c.id,
                        ),
                }
            )
            self._mappers = mappers
        return self._mappers

    def getNodesById(self, session, *ids):
        """Get nodes with specified IDs.

        ``ids`` One or more node IDs

        """
        return db.getById(self.mappers.layer_nodes, session, *ids)

    def getEdgesById(self, session, *ids):
        """Get edges with specified IDs.

        ``id`` -- One or more edges IDs

        """
        return db.getById(self.mappers.layer_edges, session, *ids)
    
    def getAdjacencyMatrix(self):
        """Return matrix. Prefer 1) existing 2) disk 3) newly created."""
        if self.G is None:
            try:
                loadfile = open(self.matrix_path, 'rb')
            except IOError:
                self.G = self.createAdjacencyMatrix()
            else:
                try:
                    self.G = marshal.load(loadfile)
                except (EOFError, ValueError, TypeError):
                    self.G = self.createAdjacencyMatrix()
                loadfile.close()
        return self.G

    def createAdjacencyMatrix(self):
        """Create the adjacency matrix for this DB's region.

        Build a matrix suitable for use with the route service. The structure
        of the matrix is defined by/in the sssp module of the route service.

        return `dict`
            Adjacency matrix for this region
            Matrix: [nodes: {}, edges: {}]
            Nodes: {v: {v: e, v: e, ...}, v: {v: e, v: e, ...}, ...}
            streets: {e: (attrs), e: (attrs), ...}

        """
        import sqlalchemy
        from byCycle.util import gis, meter

        timer = meter.Timer()

        layer_edges = self.tables.layer_edges
        layer_nodes = self.tables.layer_nodes

        # Get the number of nodes
        result = layer_nodes.count().execute()
        num_nodes = result.fetchone()[0]
        result.close()

        # Get the edge attributes
        timer.start()
        print 'Fetching edge attributes...'
        cols = ['id', 'node_f_id', 'node_t_id', 'one_way', 'length(geom)']
        if len(self.edge_attrs) > 1:
            cols += self.edge_attrs[1:]
        select_ = select(cols, engine=db.engine, from_obj=[layer_edges])
        code = layer_edges.c.code
        
        # TODO: Call region subclass to get the edge filter
        select_.append_whereclause(
            ((code >= 1200) & (code < 1600)) |
            ((code >= 3200) & (code < 3300))
        )

        result = select_.execute()
        num_edges = result.rowcount
        print 'Took %s seconds.' % timer.stop()

        print '\nNumber of streets: %s' % num_edges
        print 'Number of nodes: %s' % num_nodes

        G = {'nodes': {}, 'edges': {}}
        nodes = G['nodes']
        edges = G['edges']

        timer.start()
        print
        print 'Creating adjacency matrix...'
        met = meter.Meter(num_items=num_edges, start_now=True)
        for i, row in enumerate(result):
            adjustments = self._adjustRowForMatrix(row)

            ix = row.id
            node_f_id, node_t_id = row.node_f_id, row.node_t_id
            one_way = row.one_way

            # 0 => no travel in either direction
            # 1 => travel FT only
            # 2 => travel TF only
            # 3 => travel in both directions
            ft = one_way & 1
            tf = one_way & 2

            entry = [self.encodeFloat(row.length)]
            entry += [row[a] for a in self.edge_attrs[1:]]
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

            met.update(i+1)
        result.close()
        print '\nTook %s seconds.' % timer.stop()

        timer.start()
        print '\nSaving adjacency matrix...'
        self._saveMatrix(G)
        self.G = G
        print 'Took %s seconds.' % timer.stop()

        return G

    def encodeFloat(self, f):
        """Encode the float ``f`` as an integer."""
        return int(math.floor(f * self.float_encode))

    def decodeFloat(self, i):
        """Decode the int ``i`` back to its original float value."""
        return i * self.float_decode
    
    def _saveMatrix(self, G):
        dumpfile = open(self.matrix_path, 'wb')
        marshal.dump(G, dumpfile)
        dumpfile.close()
        
    def _adjustRowForMatrix(self, row):
        """Make changes to ``row`` before adding it to the adjacency matrix."""
        pass

    def __str__(self):
        return '%s: %s' % (self.key, self.title)
