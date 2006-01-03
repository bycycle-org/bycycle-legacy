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
        attrs = ('feet', 'cfcc', 'bikemode', 'grade', 'lanes', 'adt', 'spd',
                 'stnameid')
        self.edge_attrs = attrs
        self.indices = {}
        for i in range(len(attrs)): self.indices[attrs[i]] = i
        
        
    def createAdjacencyMatrix(self):
        """Create this mode's adj. matrix, store it in the DB, and return it.

        Build a matrix suitable for use with the route service. The structure
        of the matrix is defined by the sssp module of the route service.

        @return G -- the adjacency matrix

        """
        # Get the edge attributes and index them by index (rowid)
        # TODO: Filter out attrs that have a "bad" CFCC (highways, etc)
        Q = 'SELECT * FROM attrs'
        self.executeDict(Q)
        rows = self.fetchAllDict()
        for row in rows:
            # convert all possible values to int or float
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
        Q = 'SELECT fnode, tnode, stnameid FROM streets'
        self.executeDict(Q)
        nrows = self.fetchAllDict()
        for i, nrow in enumerate(nrows):
            for k in nrow: nrow[k] = int(nrow[k])
            rows[i].update(nrow)
        del nrows

        G = {'nodes': {}, 'edges': {}}
        nodes = G['nodes']
        edges = G['edges']

        for row in rows:
            rowid = row['rowid']
            fnode, tnode = row['fnode'], row['tnode']
            one_way = row['one_way']
            ft = one_way & 1
            tf = one_way & 2
            entry = [row[a] for a in self.edge_attrs]
            edges[rowid] = entry
            if ft:
                if not fnode in nodes: nodes[fnode] = {}
                nodes[fnode][tnode] = rowid
            if tf:
                if not tnode in nodes: nodes[tnode] = {}
                nodes[tnode][fnode] = rowid

        ## Save a compressed representation of G
        import marshal
        out_file = open(self.matrix_path, 'wb')
        marshal.dump(G, out_file)
        out_file.close()
        return G


if __name__ == '__main__':
    md = Mode();
    G = md.createAdjacencyMatrix()
