# Milwaukee Data Mode
# 11/07/2005
from byCycle.tripplanner.model import mode
 

class Mode(mode.Mode):
    def __init__(self):
        self.dmode = 'milwaukee'
        mode.Mode.__init__(self)

        # Create an index of adjacency matrix edge attributes.
        # In other words, each edge in the matrix has attributes associated
        # with it in an ordered sequence. This index gives us a way to access
        # the attributes by name while keeping the size of the matrix smaller.
        attrs = ('length', 'cfcc', 'bikemode', 'grade', 'lanes', 'adt', 'spd',
                 'ix_streetname')
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
                        row[k] = val.strip() # no. must be a string.

        # Get the from and to node IDs of the edges and add them to their
        # respective attr rows
        Q = 'SELECT wkt_geometry, id_node_f, id_node_t, ix_streetname ' \
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
            ix = row['ix']
            id_node_f, id_node_t = row['id_node_f'], row['id_node_t']
            oneway = row['oneway']
            ft = oneway & 1
            tf = oneway & 2
            try:
                length = lengthFunc(gis.importWktGeometry(row['wkt_geometry']))
            except Exception, e:
                length = 0
                
            entry = [length] + [row[a] for a in self.edge_attrs[1:]]
            edges[ix] = entry
            if ft:
                if not id_node_f in nodes: nodes[id_node_f] = {}
                nodes[id_node_f][id_node_t] = ix
            if tf:
                if not id_node_t in nodes: nodes[id_node_t] = {}
                nodes[id_node_t][id_node_f] = ix

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
