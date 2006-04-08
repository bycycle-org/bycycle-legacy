# Pittsburgh, PA Data Mode
# 11/07/2005

import math
from byCycle.tripplanner.model import mode
 

class Mode(mode.Mode):
    def __init__(self):
        self.region = 'pittsburghpa'
#        self.edge_attrs = ['bikemode', 'up_frac', 'abs_slp', 'node_f_id']
        self.edge_attrs = ['pqi', 'no_lanes', 'bptype', 'bikeability', 'elev_f', 'elev_t'] #test
        mode.Mode.__init__(self)

    #def _fixRow(self, row):
        
        #row['up_frac'] = int(math.floor(row['up_frac'] * self.int_encode))
        #row['abs_slp'] = int(math.floor(row['abs_slp'] * self.int_encode))
        # some way to deal with slope--maybe set a fSlope and tSlope
        # be careful if null elevations have been set as 0
        # what about just avoiding steep streets?
        # could give each segment a changeElev, and then calculate
        # absolute value of slope in bicycle
        
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

#        self.edge_attrs = ['bikemode', 'up_frac', 'abs_slp', 'node_f_id']
     #   self.edge_attrs = ['pqi', 'no_lanes', 'bytype', 'bikeability'] #test


        # Create an index of adjacency matrix edge attributes.
        # In other words, each edge in the matrix has attributes associated
        # with it in an ordered sequence. This index gives us a way to access
        # the attributes by name while keeping the size of the matrix smaller.
        #slopef
        #                if elevt and elevf:
                    #changeElev = elevf - elevt
                    #if changeElev>0 and length != 0:
                     #   slope = changeElev/length

        #NEED TO CORRECT
    #    attrs = ('length', 'cfcc',
     #                  'streetname_id', 'pqi', 'no_lanes',#,
      #           'bpType', 'bikeability',
       #              'slope', 
    

        
