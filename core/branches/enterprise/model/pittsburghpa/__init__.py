"""$Id$

Description goes here.

Copyright (C) 2006 Wyatt Baldwin, byCycle.org <wyatt@bycycle.org>

All rights reserved.

TERMS AND CONDITIONS FOR USE, MODIFICATION, DISTRIBUTION

1. The software may be used and modified by individuals for noncommercial, 
private use.

2. The software may not be used for any commercial purpose.

3. The software may not be made available as a service to the public or within 
any organization.

4. The software may not be redistributed.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND 
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED 
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE 
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR 
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES 
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; 
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON 
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT 
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS 
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
# Pittsburgh, PA Data Mode
# 11/07/2005

import math
from byCycle.model import mode
 

class Mode(mode.Mode):
    def __init__(self):
        self.region = 'pittsburghpa'
        self.edge_attrs = ['pqi', 'no_lanes', 'bptype', 'bikeability', 'elev_f', 'elev_t'] #test
        mode.Mode.__init__(self)


    def _adjustRowForMatrix(self, row):
        one_way = row['one_way']
        if one_way == 'ft':
            one_way = 1
        elif one_way == 'tf':
            one_way = 2
        elif one_way == '':
            one_way = 3
        else:
            one_way = 0
        row['one_way'] = one_way
       
 
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
     #                  'street_name_id', 'pqi', 'no_lanes',#,
      #           'bpType', 'bikeability',
       #              'slope',
