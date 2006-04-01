# Portland, OR Bicycle Travel Mode
# 11/07/2005

from byCycle.tripplanner.model import portlandor


class Mode(portlandor.Mode):
    def __init__(self):
        self.tmode = "bicycle"
        portlandor.Mode.__init__(self)
        self.pct_slopes = [p*.01 for p in
                           (0,    0.65, 1.8, 3.7, 7,  12, 21,  500)]
        self.mph_up     =  (12.5, 11,   9.5, 7.5, 5,  3,  2.5, 2.5)
        self.mph_down   =  (12.5, 14,   17,  21,  26, 31, 32,  32)
 

    def getEdgeWeight(self, v, edge_attrs, prev_edge_attrs):
        """Calculate weight for edge given it & last crossed edge's attrs."""
        length = edge_attrs[self.indices["length"]] * self.int_decode
        code = edge_attrs[self.indices["code"]]
        bikemode = edge_attrs[self.indices["bikemode"]]
        slope = edge_attrs[self.indices["abs_slp"]] * self.int_decode
        upfrac = edge_attrs[self.indices["up_frac"]] * self.int_decode
        downfrac = 1 - upfrac
        node_f_id = edge_attrs[self.indices["node_f_id"]]
        streetname_id = edge_attrs[self.indices["streetname_id"]]

        ## Get time cost
        up_len = length * upfrac
        down_len = length * (1.0 - upfrac)

        if v != node_f_id: up_len, down_len = down_len, up_len

        if not slope:
            up_spd = self.mph_up[0]
            down_spd = self.mph_down[0]
        elif slope >= self.pct_slopes[-1]:
            # slope is past end
            pct_past_end = slope / self.pct_slopes[-2]
            up_spd = self.mph_up[-1] / pct_past_end     #slower
            down_spd = self.mph_down[-1] * pct_past_end #faster
        else:
            for i in range(len(self.pct_slopes)):
                l, u = self.pct_slopes[i], self.pct_slopes[i+1]
                if l <= slope <= u: break
            pct_past_l = (slope - l) / (u - l)
            fui, fuj = self.mph_up[i], self.mph_up[i+1]
            up_spd = fui - (fui - fuj) * pct_past_l
            fdi, fdj = self.mph_down[i], self.mph_down[i+1]
            down_spd = fdi + (fdj - fdi) * pct_past_l

        up_time = up_len / up_spd
        down_time = down_len / down_spd
        hours = up_time + down_time

        ## Adjust for 'perceptual time'
        if bikemode:
            # Adjust bike network street
            if   bikemode == 't': hours *= .85
            elif bikemode == 'p': hours *= .90
            elif bikemode == 'b':
                # Adjust bike lane for traffic (est. from st. type)
                if   code in (1500, 1521):      hours *=  .750  #lt
                elif code == 1450:              hours *= .8750  #mt
                elif code == 1400:              hours *= 1.000  #ht
                elif code == 1300:              hours *= 2.000  #ca
                elif 1200 <= code < 1300:       hours *= 4.000  #ca+
                elif 1100 <= code < 1200:       hours *= 8.000  #ca++
                else:                           hours *= 1000   #?
            elif bikemode == 'l': hours *= 1.00
            elif bikemode == 'm': hours *= 1.17
            elif bikemode == 'h': hours *= 1.33
            elif bikemode == 'c': hours *= 2.67
            elif bikemode == 'x': hours *= 1000
        else:
            # Adjust normal (i.e., no bikemode) street based on traffic
            # (est. from st. type)
            if code in (3200, 3230, 3240, 3250): hours *= .95
            else:
                if code in (1500, 1521):         hours *= 1.50   #lt
                elif code == 1450:               hours *= 1.75   #mt
                elif code == 1400:               hours *= 2.00   #ht
                elif code == 1300:               hours *= 4.00   #ca
                elif 1200 <= code < 1300:        hours *= 8.00   #ca+
                elif 1100 <= code < 1200:        hours *= 16.00  #ca++
                else:                            hours *= 1000   #?

        # Penalize edge if it has different street name from previous edge
        try:
            prev_ix_sn = prev_edge_attrs[self.indices['streetname_id']]
            if streetname_id != prev_ix_sn:
                hours += .005555555555555
        except TypeError:
            pass        

        return hours
