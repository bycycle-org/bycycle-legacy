# Portland, OR Bicycle Travel Mode
# 11/07/2005

from byCycle.tripplanner.model import portlandor


FASTER, SHORTER, FLATTER, SAFER, DEFAULT = range(5)


class Mode(portlandor.Mode):
    def __init__(self, tmode='bicycle', pref='', **kwargs):
        """

        @param pref A string containing the user's simple preference option.
               Can be one of default, flatter, safer, shorter, or faster.

        """
        portlandor.Mode.__init__(self)
        self.pref = (pref == '') or eval(pref.upper())
        self.pct_slopes = [p*.01 for p in
                           (0,    0.65, 1.8, 3.7, 7,  12, 21,  500)]
        self.mph_up     =  (12.5, 11,   9.5, 7.5, 5,  3,  2.5, 2.5)
        self.mph_down   =  (12.5, 14,   17,  21,  26, 31, 32,  32)
 

    def getEdgeWeight(self, v, edge_attrs, prev_edge_attrs):
        """Calculate weight for edge given it & last crossed edge's attrs."""
        length = edge_attrs[self.indices['length']] * self.int_decode
        code = edge_attrs[self.indices['code']]
        bikemode = edge_attrs[self.indices['bikemode']]
        slope = edge_attrs[self.indices['abs_slp']] * self.int_decode
        upfrac = edge_attrs[self.indices['up_frac']] * self.int_decode
        downfrac = 1 - upfrac
        node_f_id = edge_attrs[self.indices['node_f_id']]
        streetname_id = edge_attrs[self.indices['streetname_id']]
        cpd = edge_attrs[self.indices['cpd']]
 

        # -- Calculate base weight of edge (in hours)
        

        # Length of segment that is uphill in from => to direction
        up_len = length * upfrac

        # Length of segment that is downhill in from => to direction
        down_len = length * (1.0 - upfrac)

        # Swap uphill and downhill lengths when traversing segment to => from
        if v != node_f_id:
            up_len, down_len = down_len, up_len

        # Based on the slope, calculate the speed of travel uphill and downhill
        # (up_spd & down_spd)
        if slope <= 0:
            up_spd = self.mph_up[0]
            down_spd = self.mph_down[0]
        elif slope >= self.pct_slopes[-1]:
            # Slope is past end
            pct_past_end = slope / self.pct_slopes[-2]
            up_spd = self.mph_up[-1] / pct_past_end     #slower
            down_spd = self.mph_down[-1] * pct_past_end #faster
        else:
            for i, u in enumerate(self.pct_slopes[1:]):
                if slope <= u:
                    l = self.pct_slopes[i]
                    break
            pct_past_l = (slope - l) / (u - l)
            mph_up_i, mph_up_j = self.mph_up[i], self.mph_up[i+1]
            up_spd = mph_up_i - (mph_up_i - mph_up_j) * pct_past_l
            mph_down_i, mph_down_j = self.mph_down[i], self.mph_down[i+1]
            down_spd = mph_down_i + (mph_down_j - mph_down_i) * pct_past_l

        # Based on uphill length and speed, calculate time to traverse uphill
        # part of segment
        up_time = up_len / up_spd
        # Likewise for downhill part of segment
        down_time = down_len / down_spd
        # Add those together for estimated total time to traverse segment
        hours = up_time + down_time


        # -- Adjust weight based on user preference

        # Multiply bike lane values by `mult` to get non-network weights
        if self.pref == SAFER:
            mult = 3
            t = .75
            p = .8
            c = 4
        else:
            mult = 2
            t = .85
            p = .9
            c = 2.67
            
        # no bike lane
        l = 1
        m = 1.17
        h = 1.33
        x = 1000
        # bike lane
        bl = .75
        bm = .875
        bh = 1
        bc = 2
        bcc = 4
        bccc = 8            
        
        # Adjust for 'perceptual time'
        if bikemode:
            # Adjust bike network street
            if   bikemode == 't': hours *= t
            elif bikemode == 'p': hours *= p
            elif bikemode == 'b':
                # Adjust bike lane for traffic (est. from st. type)
                if   code in (1500, 1521):      hours *= bl    #lt
                elif code == 1450:              hours *= bm    #mt
                elif code == 1400:              hours *= bh    #ht
                elif code == 1300:              hours *= bc    #ca
                elif 1200 <= code < 1300:       hours *= bcc   #ca+
                elif 1100 <= code < 1200:       hours *= bccc  #ca++
                else:                           hours *= x     #?          
            elif bikemode == 'l': hours *= l
            elif bikemode == 'm': hours *= m
            elif bikemode == 'h': hours *= h
            elif bikemode == 'c': hours *= c
            elif bikemode == 'x': hours *= x
        else:
            # Adjust normal (i.e., no bikemode) street based on traffic
            # (est. from st. type)
            if code == 3200:                     hours *= t
            elif code in (3230, 3240, 3250):  hours *= p
            else:
                if code in (1500, 1521):         hours *= bl * mult    #lt
                elif code == 1450:               hours *= bm * mult    #mt
                elif code == 1400:               hours *= bh * mult    #ht
                elif code == 1300:               hours *= bc * mult    #ca
                elif 1200 <= code < 1300:        hours *= bcc * mult   #ca+
                elif 1100 <= code < 1200:        hours *= bccc * mult  #ca++
                else:                            hours *= x * mult     #?


        # Penalize edge if it has different street name from previous edge
        try:
            prev_ix_sn = prev_edge_attrs[self.indices['streetname_id']]
            if streetname_id != prev_ix_sn:
                hours += .005555555555555  # 20 seconds
        except TypeError:
            pass        

        return hours
