"""$Id$

Portland, OR Data Mode (11/07/2005).

Copyright (C) 2006 Wyatt Baldwin, byCycle.org <wyatt@bycycle.org>. All rights 
reserved. Please see the LICENSE file included in the distribution. The license 
is also available online at http://bycycle.org/tripplanner/license.txt or by 
writing to license@bycycle.org.

"""
import sys
sys.path.append('/home/bycycle/byCycle/evil')


import math
from byCycle.model import mode
 

class Mode(mode.Mode):
    def __init__(self):
        self.name = 'portlandor'
        self.region = 'portlandor'
        self.edge_attrs = ['bikemode', 'up_frac', 'abs_slp', 'node_f_id',
                           'cpd']
        mode.Mode.__init__(self)
        #self.mode = mode.Mode(self)

    def _adjustRowForMatrix(self, row):
        row['up_frac'] = int(math.floor(row['up_frac'] * self.int_encode))
        row['abs_slp'] = int(math.floor(row['abs_slp'] * self.int_encode))


if __name__ == '__main__':
    import time
    from byCycle.lib import meter
    
    md = Mode();
    
    t = meter.Timer()
    G1 = md.createAdjacencyMatrix()
    print t.stop()

