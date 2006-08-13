# Portland, OR Data Mode
# 11/07/2005

import sys
sys.path.insert(0, '/home/bycycle/byCycle/evil')


import math
from byCycle.tripplanner.model import mode
 

class Region(object):
    def __init__(self):
        self.name = 'portlandor'
        self.edge_attrs = ['bikemode', 'up_frac', 'abs_slp', 'node_f_id',
                           'cpd']
        self.mode = mode.Mode(self)
        

    def _adjustRowForMatrix(self, row):
        row['up_frac'] = int(math.floor(row['up_frac'] * self.mode.int_encode))
        row['abs_slp'] = int(math.floor(row['abs_slp'] * self.mode.int_encode))


if __name__ == '__main__':
    import time
    from byCycle.lib import meter
    md = mode.Mode(Region());
    
    t = meter.Timer()
    #G1 = md.createAdjacencyMatrix()
    #print t.stop()

    print 'Getting adjacency matrix...'

    for i in range(10):
        t.start()
        G2 = md.getAdjacencyMatrix()
        print t.stop()

    print G2[0][1]
    print G2[1][3]
