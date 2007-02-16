"""$Id: __init__.py 194 2006-08-17 19:30:46Z bycycle $

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

import sys
sys.path.insert(0, '/home/dacc/byCycle')

import math
from byCycle.model import mode
 

class Mode(mode.Mode):
    def __init__(self):
        self.region = 'seattlewa'
        self.edge_attrs = ['bikeclass', 'node_f_id']
        mode.Mode.__init__(self)

    def _adjustRowForMatrix(self, row):
      pass

if __name__ == '__main__': 
    import time
    from byCycle.util import meter
    
    t = meter.Timer()
    md = Mode();
    
    G1 = md.createAdjacencyMatrix()
    assert(isinstance(G1, dict))
    
    t.start()
    print 'Getting adjacency matrix...'
    G2 = md.getAdjacencyMatrix()
    print t.stop()
    
    print G2['edges'].popitem()
