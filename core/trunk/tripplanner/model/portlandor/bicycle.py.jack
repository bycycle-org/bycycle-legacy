# Portland, OR Bicycle Travel Mode
# 11/07/2005
from byCycle.tripplanner.model import portlandor
FASTER, SHORTER, FLATTER, SAFER, DEFAULT = range(5)
class Mode(portlandor.Mode):
    def __init__(self, tmode='bicycle', pref='', **kwargs):
        """
          @param pref A string containing the user's simple preference option.
          Can be one of default, flatter, safer, shorter, or faster. """
        portlandor.Mode.__init__(self)
        self.pref = (pref == '') or eval(pref.upper())
        self.pct_slopes = [p*.01 for p in
                           (0,    0.65, 1.8, 3.7, 7,  12, 21,  500)]
        self.mph_up     =  (12.5, 11,   9.5, 7.5, 5,  3,  2.5, 2.5)
        self.mph_down   =  (12.5, 14,   17,  21,  26, 31, 32,  32)
 

    def getEdgeWeight(self, v, edge_attrs, prev_edge_attrs):
        """Calculate weight for edge given it & last crossed edge's attrs."""
        miles = edge_attrs[self.indices['length']] * self.int_decode
        code = edge_attrs[self.indices['code']]
        bikemode = edge_attrs[self.indices['bikemode']]
        slope = edge_attrs[self.indices['abs_slp']] * self.int_decode
        upfrac = edge_attrs[self.indices['up_frac']] * self.int_decode
        node_f_id = edge_attrs[self.indices['node_f_id']]
        cpd = edge_attrs[self.indices['cpd']]
        up_mi, down_mi = miles * upfrac, miles * (1.0 - upfrac)
        # Swap uphill and downhill lengths when traversing segment to => from
        if v != node_f_id: up_mi, down_mi = down_mi, up_mi
        if slope <= 0: # slope = 0 (abs_slp mustn't be -ve)
            up_mph = self.mph_up[0]
            down_mph = self.mph_down[0]
        elif slope >= self.pct_slopes[-1]: # Slope is out of range
            pct_past_end = slope / self.pct_slopes[-2]
            up_mph = self.mph_up[-1] / pct_past_end     #slower
            down_mph = self.mph_down[-1] * pct_past_end #faster
        else: # slope in expected range, interpolate
            for i, u in enumerate(self.pct_slopes[1:]):
                if slope <= u:
                    l = self.pct_slopes[i]
                    break
            pct_past_l = (slope - l) / (u - l)
            mph_up_i, mph_up_j = self.mph_up[i], self.mph_up[i+1]
            up_mph = mph_up_i - (mph_up_i - mph_up_j) * pct_past_l
            mph_down_i, mph_down_j = self.mph_down[i], self.mph_down[i+1]
            down_mph = mph_down_i + (mph_down_j - mph_down_i) * pct_past_l
        hours = (up_mi / up_mph) + (down_mi / down_mph)
        cpt = cpd * hours /24 # cars/traversal
        ftUp = up_mi * slope * 5280
        # set blend fractions (for now) from enumerated
        if self.pref == FASTER: fMi, fHrs, fFtUp, fCPT = .1, .7, .1, .1
        elif self.pref == SHORTER: fMi, fHrs, fFtUp, fCPT = .7, .1, .1, .1
        elif self.pref == FLATTER: fMi, fHrs, fFtUp, fCPT = .1, .1, .7, .1
        else: fMi, fHrs, fFtUp, fCPT = .1, .1, .1, .7 # SAFER, DEFAULT
        # factor in normalizing weights for 4 basic costs (divide by sums
        # of Excel's 1st 64k records in str04aug.dbf)
        fMi, fHrs, fFtUp, fCPT = fMi/6000, fHrs/566, fFtUp/530000, fCPT/66000
        return (fMi*miles) + (fHrs*hours) + (fFtUp*ftUp) + (fCPT*cpt)
if __name__ == "__main__": # jkn, to help understand...
    from byCycle.tripplanner.model.portlandor import bicycle
    m = bicycle.Mode()
    G = m.getAdjacencyMatrix()
    v, d = G['nodes'].popitem()
    v, d = G['nodes'].popitem()
    v, d = G['nodes'].popitem()
    e0, e1 = d.keys()[0:2]
    edge_attrs = G['edges'][e0]
    print "e0 =", e0
    prev_edge_attrs = G['edges'][e1]
    # print edge_attrs: (1L, (378931, 1500, 1L, '', 346000, 14000, 22003L, 432L))
    # =>    (mi=.378931, code=1500, upFrc=.346, slope=.014, 22003L, cpd=432))

    print m.getEdgeWeight(v, edge_attrs, prev_edge_attrs)