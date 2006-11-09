###########################################################################
# $Id$
# Created 2005-11-07.
#
# Database Abstraction Layer.
#
# Copyright (C) 2006 Wyatt Baldwin, byCycle.org <wyatt@bycycle.org>.
# All rights reserved.
#
# For terms of use and warranty details, please see the LICENSE file included
# in the top level of this distribution. This software is provided AS IS with
# NO WARRANTY OF ANY KIND.


"""Database initialization and handling.

TODO:
  - Use fancy-pants ORM (SQLAlchemy, for example) to create proper model/domain
    objects.
  - Decouple regions from this class (i.e., they shouldn't be subclasses)--when
    moving to using an ORM, move the region-common stuff into a Region base
    class.
  - Make createAdjacencyMatrix available through bycycle script.
  - Should DB class be a Singleton (per region)???

"""
from os.path import join as os_path_join
import math

import psycopg2
import psycopg2.extensions

from sqlalchemy.engine import create_engine
from sqlalchemy.schema import BoundMetaData
from sqlalchemy.sql import select
from sqlalchemy.orm import create_session, mapper, relation

from byCycle import install_path
from byCycle.lib import util
from byCycle.model.domain import *


### Some "constants"

# The number of digits to save when encoding a float as an int
float_exp = 6
# Multiplier to create int-encoded float
float_encode = 10 ** float_exp
# Multiplier to get original float value back
float_decode = 10 ** -float_exp


### Database initialization

# Path to model package
path = os_path_join(install_path, 'model')

# database-table <==> domain-object mappers
mappers = {}
tables = {}

def createConnection(path=path, host='localhost', database='bycycle',
                     user='bycycle'):
    """Set up and return underlying DB connection."""
    pw_path = os_path_join(path, '.pw')
    pw_file = file(pw_path)
    pw = pw_file.read().strip()
    pw_file.close()
    return psycopg2.connect(
        database=database,
        user=user,
        password=pw
    )

engine = create_engine('postgres://',creator=createConnection)
metadata = BoundMetaData(engine)
raw_metadata = BoundMetaData(engine)
session = create_session(bind_to=engine)


class DB(object):
    """A database handler for a specific region."""

    def __init__(self, region):
        """Create a database handler for ``region``.

        ``region`` `Region`

        """
        self.region = region
        self.schema = region.key

        # Connect to database
        self.engine = engine
        self.connection = engine.raw_connection()
        self.cursor = self.connection.cursor()
        self.metadata = metadata
        self.raw_metadata = raw_metadata
        self.session = session

        # Create object<->table mappers
        self.__initMappers()

        # Set up path to data files
        self.data_path = os_path_join(path, self.schema, 'data')
        self.matrix_path = os_path_join(self.data_path, 'matrix.pyc')
        
        self.float_encode = float_encode
        self.float_decode = float_decode

    def _get_tables(self):
        """Create schema tables, iff they haven't been already."""
        schema = self.schema
        if schema not in tables:
            imp_path = 'byCycle.model.%s.data.tables' % schema
            tables_mod = __import__(imp_path, globals(), locals(), [''])
            tables[schema] = tables_mod.Tables(schema, metadata, raw_metadata)
        return tables[schema]
    tables = property(_get_tables)

    def __initMappers(self):
        """Initialize database-table <==> domain-object mappers."""
        schema = self.schema
        try:
            _ms = mappers[schema]
        except KeyError:
            mappers[schema] = {}
            _ms = mappers[schema]

            tables = self.tables
            layer_nodes = tables.layer_nodes
            street_names = tables.street_names
            cities = tables.cities
            states = tables.states
            layer_edges = tables.layer_edges
            
            edges_c = layer_edges.c
            nodes_c = layer_nodes.c
            
            _ms['layer_nodes'] = mapper(
                Node,
                layer_nodes,
                properties={
                    'edges': relation(
                        Edge,
                        primaryjoin=(
                            (nodes_c.id == edges_c.node_f_id) | 
                            (nodes_c.id == edges_c.node_t_id)
                        )
                    )
                }
            )

            _ms['street_names'] = mapper(
                StreetName,
                street_names,
            )

            _ms['cities'] = mapper(
                City,
                cities,
            )

            _ms['states'] = mapper(
                State,
                states,
            )

            _ms['layer_edges'] = mapper(
                Edge,
                layer_edges,
                properties={
                    'node_f': relation(
                        Node,
                        primaryjoin=edges_c.node_f_id == nodes_c.id,
                        ),
                    'node_t': relation(
                        Node,
                        primaryjoin=edges_c.node_t_id == nodes_c.id,
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
        # Add mappers to self with names of the form tablename_mapper
        names = ('layer_nodes','street_names','cities','states','layer_edges')
        for name in names:
            mapper_name = '%s_mapper' % name
            try:
                getattr(self, mapper_name)
            except AttributeError:
                setattr(self, mapper_name, _ms[name])

    ### Utility Methods

    def turnSQLEchoOff(self):
        """Turn off echoing of SQL statements."""
        engine.echo = False

    def turnSQLEchoOn(self):
        """Turn on echoing of SQL statements."""
        engine.echo = True

    def vacuum():
        """Vacuum all tables."""
        self.connection.set_isolation_level(0)
        self.cursor.execute('VACUUM FULL ANALYZE')
        self.connection.set_isolation_level(2)

    ### Node Methods

    def getNodesById(self, ids):
        """Get nodes with specified IDs.

        ``id`` `list` | `int` -- A `list` of node IDs or a single ID

        return `Session`, `list`
            The `Session` we're fetching the nodes within and a `list` of
            `Node`s

        """
        return self.getById(
            ids, self.layer_nodes_mapper, self.tables.layer_nodes
        )
        
    ### Edge Methods

    def getEdgesById(self, ids, session=None):
        """Get edges with specified IDs.

        ``id`` `list` | `int` -- A `list` of edges IDs or a single ID

        return `Session`, `list`
            The `Session` we're fetching the edges within and a `list` of
            `Streets`s

        """
        return self.getById(
            ids, self.layer_edges_mapper, self.tables.layer_edges
        )
    
    ### Adjacency Matrix Methods

    def getAdjacencyMatrix(self, force_new=False):
        """Return matrix. Prefer 1) existing 2) disk 3) newly created."""
        import marshal
        if force_new:
            self.region.G = self._createAdjacencyMatrix()
        elif self.region.G is None:
            try:
                loadfile = open(self.matrix_path, 'rb')
            except IOError:
                self.region.G = self._createAdjacencyMatrix()
            else:
                try:
                    self.region.G = marshal.load(loadfile)
                except:  # FIXME: Except what?
                    self.region.G = self._createAdjacencyMatrix()
                loadfile.close()
        return self.region.G

    def _createAdjacencyMatrix(self):
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
        from byCycle.lib import gis, meter

        t = meter.Timer()
        layer_edges = self.tables.layer_edges
        layer_nodes = self.tables.layer_nodes

        # Get the number of nodes
        print 'Fetching node count...'
        result = layer_nodes.count().execute()
        num_nodes = result.fetchone()[0]
        result.close()

        # Get the edge attributes
        t.start()
        print 'Fetching edge attributes...'
        cols = ['id', 'node_f_id', 'node_t_id', 'one_way', 'length(geom)']
        if len(self.region.edge_attrs) > 1:
            cols += self.region.edge_attrs[1:]
        select_ = select(cols, engine=self.engine, from_obj=[layer_edges])
        result = select_.execute()
        num_edges = result.rowcount
        print 'Took %s' % t.stop()

        print 'Number of streets: %s' % num_edges
        print 'Number of nodes: %s' % num_nodes

        G = {'nodes': {}, 'edges': {}}
        nodes = G['nodes']
        edges = G['edges']

        print 'Creating adjacency matrix...'
        met = meter.Meter(num_items=num_edges, start_now=True)
        for i, row in enumerate(result):
            adjustments = self.region._adjustRowForMatrix(self, row)

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
            entry += [row[a] for a in self.region.edge_attrs[1:]]
            for k in adjustments:
                entry[self.region.edge_attrs_index[k]] = adjustments[k]
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
        print
        result.close()

        t.start()
        print 'Saving adjacency matrix...'
        self._saveMatrix(G)
        self.region.G = G
        print 'Took %s.' % t.stop()
        return G

    def _saveMatrix(self, G):
        import marshal
        dumpfile = open(self.matrix_path, 'wb')
        marshal.dump(G, dumpfile)
        dumpfile.close()

    ### Utility Methods

    def getById(self, ids, mapper, table):
        """Get objects from ``table`` using mapper and order them by ``ids``.
        
        ``ids`` `list` | `int` -- A list of row IDs or a single ID
        ``mapper`` -- DB to object mapper
        ``table`` -- Table to fetch from
        
        """
        try: 
            i = int(ids)
        except: 
            pass
        else: 
            ids = [i]
        query = self.session.query(mapper)
        objects = query.select(table.c.id.in_(*ids))
        objects_by_id = dict(zip([object.id for object in objects], objects))
        ordered_objects = []
        for i in ids:
            try:
                ordered_objects.append(objects_by_id[i])
            except KeyError:
                # TODO: Should we insert None instead???
                pass
        return ordered_objects    
    
    def encodeFloat(self, f):
        """Encode the float ``f`` as an integer."""
        return int(math.floor(f * float_encode))

    def decodeFloat(self, i):
        """Decode the int ``i`` back to its original float value."""
        return i * float_decode


if __name__ == "__main______________________":
    from byCycle.model import portlandor
    r = portlandor.Region()
    db = DB(r)
    ids = [1, 6, 245, 1002, 2050, 10004, 10000000]
    session, objects = db.getEdgesById(*[ids])
    for s in objects:
        print s
        print s.node_f, s.node_t
        print
    session.close()
    # Nodes
    ids = [1, 6, 245, 1002, 2050, 10004, 10000000]
    session, objects = db.getNodesById(*[ids])
    for o in objects:
        print o
        print
    session.close()

if __name__ == '__main__':
    from byCycle.lib import meter
    from byCycle.model import portlandor
    r = portlandor.Region()
    db = DB(r)
    t = meter.Timer()
    G = db.getAdjacencyMatrix(force_new=1)
    print 'Time to get G: ', t.stop()
    print 'Number of streets in G:', len(G['edges'])
    print 'Number of nodes in G:', len(G['nodes'])
    print r.edge_attrs
    item = G['edges'].popitem()
    print item
    while item[1][1] is None:
        item = G['edges'].popitem()
    print item


'''
    ### Experimental

    def createAdjacencyMatrixListType(self):
        """Create this region's adjacency matrix, serialize it, and return it.

        Build a matrix suitable for use with the route service. The structure
        of the matrix is defined by/in the sssp module of the route service.

        Return `list`
            Adjacency matrix for a given region. Instead of explicit IDs, list
            indices are used as the node and edge IDs.
            Matrix: [[Nodes], [streets]]
            Nodes: [[v, e], [v, e], ...], [[], [], ...], ...
            streets: [[attrs], [attrs], ...]

        """
        from byCycle.lib import gis, meter

        timer = meter.Timer()
        tables = self.tables

        # Get the number of nodes
        Q = 'SELECT COUNT(*) FROM %s' % tables.layer_nodes
        self.execute(Q)
        num_nodes = self.fetchRow()[0]

        # Get the street attributes
        timer.start()
        print 'Fetching edge attributes...'
        Q = 'SELECT id, node_f_id, node_t_id, one_way, ' \
            '%s, ' \
            'AsText(geom) AS wkt_geometry ' \
            'FROM %s ' \
            'ORDER BY id' % \
            (', '.join(self.edge_attrs[1:]), tables.layer_edges)
        print Q
        self.executeDict(Q)
        rows = self.fetchAllDict()
        num_edges = len(rows)
        print 'Took %s' % timer.stop()

        print 'Number of streets: %s' % num_edges
        print 'Number of nodes: %s' % num_nodes

        G = ([[] for i in range(num_nodes+1)],
             [[] for i in range(num_edges+1)])
        nodes = G[0]
        streets = G[1]

        print 'Creating adjacency matrix...'
        meter = meter.Meter(num_items=num_edges, start_now=True)
        for i, row in enumerate(rows):
            self._adjustRowForMatrix(self, row)

            ix = int(row.id)
            node_f_id = int(row.node_f_id)
            node_t_id = int(row.node_t_id)

            # 0 => no travel in either direction
            # 1 => travel FT only
            # 2 => travel TF only
            # 3 => travel in both directions
            one_way = row.one_way
            ft = one_way & 1
            tf = one_way & 2

            linestring = importWktGeometry(row.wkt_geometry)
            length = getLengthOfLineString(linestring)
            length = int(math.floor(length * self.int_encode))
            row.length = length

            attrs = [row[a] for a in self.edge_attrs]
            for i, a in enumerate(attrs):
                if isinstance(a, long):
                    attrs[i] = int(attrs[i])
            streets[ix] = tuple(attrs)

            if ft:
                nodes[node_f_id].append((node_t_id, ix))
            if tf:
                nodes[node_t_id].append((node_f_id, ix))

            meter.update(i+1)

        nodes = [tuple(v_list) or None for v_list in nodes]
        streets = [attrs or None for attrs in streets]
        G = tuple(G)

        timer.start()
        print '\nSaving adjacency matrix...'
        self._saveMatrix(G)
        self.region.G = G
        print 'Took %s' % timer.stop()
        return G
'''