# Portland, OR Data Mode
# 11/07/2005

from byCycle.tripplanner.model import mode
 

class Mode(mode.Mode):
    def __init__(self):
        self.region = 'portlandor'
        mode.Mode.__init__(self)

        # Create an index of adjacency matrix edge attributes.
        # In other words, each edge in the matrix has attributes associated
        # with it in an ordered sequence. This index gives us a way to access
        # the attributes by name while keeping the size of the matrix smaller.
        attrs = ('length', 'code', 'bikemode', 'up_frac', 'abs_slp',
                 'streetname_id', 'node_f_id')
        self.edge_attrs = attrs
        self.indices = {}
        for i in range(len(attrs)): self.indices[attrs[i]] = i
        
        
    def createAdjacencyMatrix(self):
        """Create this mode's adj. matrix, store it in the DB, and return it.

        Build a matrix suitable for use with the route service. The structure
        of the matrix is defined by the sssp module of the route service.

        @return G -- the adjacency matrix

        """
        from byCycle.lib import gis, meter
        import math

        lengthFunc = gis.getLengthOfLineString
        
        # Get the edge attributes
        Q = 'SELECT * FROM %s' % self.tables['street_attrs']
        self.executeDict(Q)
        rows = self.fetchAllDict()
        # Convert all possible values to int or float
        for row in rows:
            for k in row: 
                val = row[k]
                try:
                    row[k] = int(val)        # int?
                except ValueError:
                    try:
                        row[k] = float(val)  # no. float?
                    except ValueError:
                        row[k] = str(val.strip()) # no. must be a string.

        # Get the from and to node IDs of the edges and add them to their
        # respective attr rows
        Q = 'SELECT wkt_geometry, node_f_id, node_t_id, streetname_id ' \
            'FROM %s' % self.tables['edges']
        self.executeDict(Q)
        nrows = self.fetchAllDict()
        for i, nrow in enumerate(nrows):
            for k in nrow:
                try:
                    nrow[k] = int(nrow[k])
                except ValueError:
                    pass
            rows[i].update(nrow)
        del nrows

        G = {'nodes': {}, 'edges': {}}
        nodes = G['nodes']
        edges = G['edges']

        met = meter.Meter()
        met.setNumberOfItems(len(rows))
        met.startTimer()
        record_number = 1
        
        for row in rows:
            ix = row['id']
            node_f_id, node_t_id = row['node_f_id'], row['node_t_id']

            oneway = row['oneway']
            both_ways = oneway == ''
            ft = both_ways or (oneway == 'f')
            tf = both_ways or (oneway == 't')

            length = int(math.floor(lengthFunc(gis.importWktGeometry(row['wkt_geometry'])) *
                                    1000000))

            row['up_frac'] = int(math.floor(row['up_frac'] * 1000000))
            row['abs_slp'] = int(math.floor(row['abs_slp'] * 1000000))
            
            entry = [length] + [row[a] for a in self.edge_attrs[1:]]
            edges[ix] = entry
            
            if ft:
                if not node_f_id in nodes: nodes[node_f_id] = {}
                nodes[node_f_id][node_t_id] = ix
            if tf:
                if not node_t_id in nodes: nodes[node_t_id] = {}
                nodes[node_t_id][node_f_id] = ix

            met.update(record_number)
            record_number+=1
        print
            
        ## Save a compressed representation of G
        import marshal
        out_file = open(self.matrix_path, 'wb')
        marshal.dump(G, out_file)
        out_file.close()
        return G


if __name__ == '__main__':
    md = Mode();
    G = md.createAdjacencyMatrix()
