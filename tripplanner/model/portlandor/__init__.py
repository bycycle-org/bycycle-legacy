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
        from byCycle.lib import meter
        import math
        
        # Get the edge attributes
        t = meter.Timer()
        t.start()
        print 'Fetching edge attributes...'
        Q = 'SELECT id, node_t_id, one_way, ' \
            '%s, ' \
            'GLength(geom) AS length ' \
            'FROM %s' % (', '.join(self.edge_attrs[1:]), self.tables['edges'])
        self.executeDict(Q)
        rows = self.fetchAllDict()
        print 'Took %s' % t.stop()
        
        # Convert all possible values to int or float
        print 'Converting values to int or float...'
        met = meter.Meter(num_items=len(rows), start_now=True)
        i = 1
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
            met.update(i)
            i+=1
        print

        G = {'nodes': {}, 'edges': {}}
        nodes = G['nodes']
        edges = G['edges']

        print 'Creating adjacency matrix...'
        met.setNumberOfItems(len(rows)); met.startTimer(); i = 1
        for row in rows:
            ix = row['id']
            node_f_id, node_t_id = row['node_f_id'], row['node_t_id']

            one_way = row['one_way']
            both_ways = one_way == ''
            ft = both_ways or (one_way == 'f')
            tf = both_ways or (one_way == 't')

            row['up_frac'] = int(math.floor(row['up_frac'] * 1000000))
            row['abs_slp'] = int(math.floor(row['abs_slp'] * 1000000))

            length = int(math.floor(row['length']) * 1000000)
            
            entry = [length] + [row[a] for a in self.edge_attrs[1:]]
            edges[ix] = entry
            
            if ft:
                if not node_f_id in nodes: nodes[node_f_id] = {}
                nodes[node_f_id][node_t_id] = ix
            if tf:
                if not node_t_id in nodes: nodes[node_t_id] = {}
                nodes[node_t_id][node_f_id] = ix

            met.update(i)
            i+=1
        print
        
        t.start()
        print 'Saving adjacency matrix...'
        self._saveMatrix(G)
        self.G = G
        print 'Took %s' % t.stop()
        return G


if __name__ == '__main__':
    import time
    from byCycle.lib import meter
    
    t = meter.Timer()
    
    md = Mode();
    
    G1 = md.createAdjacencyMatrix()
    
    assert(isinstance(G1, dict))
    
    t.start()
    print 'Getting adjacency matrix...'
    G2 = md.getAdjacencyMatrix()
    print t.stop()
    
    print G2['edges'].popitem()
    
    assert(isinstance(G2, dict))
    assert(G1 == G2)
