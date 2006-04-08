# Portland, OR Data Mode
# 11/07/2005

import math
from byCycle.tripplanner.model import mode
 

class Mode(mode.Mode):
    def __init__(self):
        self.region = 'portlandor'
        self.edge_attrs = ['bikemode', 'up_frac', 'abs_slp', 'node_f_id',
                           'cpd']
        mode.Mode.__init__(self)
        

    def _fixRow(self, row):
        row['up_frac'] = int(math.floor(row['up_frac'] * self.int_encode))
        row['abs_slp'] = int(math.floor(row['abs_slp'] * self.int_encode))


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
