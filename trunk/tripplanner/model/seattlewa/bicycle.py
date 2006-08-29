"""$Id: bicycle.py 197 2006-08-28 23:52:22Z bycycle $

Seattle, WA Travel Mode

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
from byCycle.tripplanner.model import seattlewa

class BikeDesignation:
  NOT_DESIGNATED, PATH, LANE, URBAN_CONNECTOR, NEIGHBORHOOD_CONNECTOR = range(5)

class DesignationWeightMap(dict):
  __init__(self):
    # avoid anything without any designation
    self[ BikeDesignation.NOT_DESIGNATED ] = 1000;

    # bike paths are the most preferable route
    self[ BikeDesignation.PATH ] = .75;

    # lanes are the next best thing
    self[ BikeDesignation.PATH ] = .9;

    # not sure what these will mean...
    self[ BikeDesignation.URBAN_CONNECTOR ] = 1;
    self[ BikeDesignation.NEIGHBORHOOD_CONNECTOR ] = 1;

class Mode(seattlewa.Mode):
    def __init__(self, tmode='bicycle', **kwargs):
        seattlewa.Mode.__init__(self)

        self.avg_mph = 10

#        self.pct_slopes = [p*.01 for p in
#                           (0,    0.65, 1.8, 3.7, 7,  12, 21,  500)]
#        self.mph_up     =  (12.5, 11,   9.5, 7.5, 5,  3,  2.5, 2.5)
#        self.mph_down   =  (12.5, 14,   17,  21,  26, 31, 32,  32)

    def getEdgeWeight(self, v, edge_attrs, prev_edge_attrs):
        """Calculate weight for edge given it & last crossed edge's attrs."""
        length = edge_attrs[self.indices['length']] * self.int_decode
        bikeclass = edge_attrs[self.indices['bikeclass']]
        node_f_id = edge_attrs[self.indices['node_f_id']]
        streetname_id = edge_attrs[self.indices['streetname_id']]
 
        # TODO: implement slope awareness
        hours = length * self.avg_mph;

        map = DesignationWeightMap()
        hours *= map[ bikeclass ]

        # Penalize edge if it has different street name from previous edge
        try:
            prev_ix_sn = prev_edge_attrs[self.indices['streetname_id']]
            if streetname_id != prev_ix_sn:
                hours += .0027777  # 10 seconds
        except TypeError:
            pass        

        return hours

