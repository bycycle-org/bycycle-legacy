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
