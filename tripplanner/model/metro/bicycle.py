# 11/07/2005

import __init__

class Mode(__init__.Mode):
    def __init__(self):
        self.mode = "bicycle"
        __init__.Mode.__init__(self)
        self.pct_slopes = [p*.01 for p in
                           (0,   0.65, 1.8, 3.7, 7,  12, 21,  500)]
        self.fpm_up  =    [m*(5280/60) for m in
                           (12.5, 11,   9.5, 7.5, 5,  3,  2.5, 2.5)]
        self.fpm_down =   [m*(5280/60) for m in
                           (12.5, 14,   17,  21,  26, 31, 32,  32)]
 

    def getEdgeWeight(self, e, E, G_edges):
        edge = G_edges[e]
        base_weight = edge[self.indices["weight"]]

        upfrac = edge[self.indices["upfrac"]]
        up_len = base_weight * upfrac
        down_len = base_weight * (1.0 - upfrac)

        slope = edge[self.indices["slope"]]

        if not slope:
            up_spd = self.fpm_up[0]
            down_spd = self.fpm_down[0]
        elif slope >= self.pct_slopes[-1]:
            # slope is past end
            pct_past_end = slope / self.pct_slopes[-2]
            up_spd = self.fpm_up[-1] / pct_past_end     #slower
            down_spd = self.fpm_down[-1] * pct_past_end #faster
        else:
            for i in range(len(self.pct_slopes)):
                l, u = self.pct_slopes[i], self.pct_slopes[i+1]
                if l <= slope <= u: break
            pct_past_l = (slope - l) / (u - l)
            fui, fuj = self.fpm_up[i], self.fpm_up[i+1]
            up_spd = fui - (fui - fuj) * pct_past_l 
            fdi, fdj = self.fpm_down[i], self.fpm_down[i+1]
            down_spd = fdi + (fdj - fdi) * pct_past_l
            
        up_time = up_len / up_spd
        down_time = down_len / down_spd
        total_time = up_time + down_time

        try: last_edge = G_edges[E[-1]]
        except IndexError: pass
        else:
            # Penalize the edge if it has a different street name from the
            # previous edge
            stid_idx = self.indices["stid"] 
            stid = edge[stid_idx]
            prev_stid = last_edge[stid_idx]
            if stid != prev_stid: total_time += 0
        
        return total_time


    def _getLeastTrafficWeight(self):
        edge = G_edges[e]

        base_weight = edge[self.indices["weight"]]
        flags = edge[self.indices["flags"]]
        code = edge[self.indices["code"]]

        cf = self.flags
        bikemode = 0
        
        for bm in self.bikemodes:
            # Figure out the segment's bikemode...
            bikemode = flags & cf[bm]
            if bikemode:
                # ...and then penalize it
                if   bikemode == cf["mu"]: base_weight *= 1
                elif bikemode == cf["mm"]: base_weight *= 2
                elif bikemode == cf["bl"]:
                    base_weight *= 4
                    # Penalize bike lane for traffic (est. from st. type)
                    if   code in (1500, 1521):     base_weight *= 1   #lt
                    elif code == 1450:             base_weight *= 2   #mt
                    elif code == 1400:             base_weight *= 4   #ht
                    elif code == 1300:             base_weight *= 8   #ca
                    elif 1200 <= code < 1300:      base_weight *= 16  #ca+
                    elif 1100 <= code < 1200:      base_weight *= 32  #ca++
                    else:                          base_weight *= 64  #?
                elif bikemode == cf["lt"]: base_weight *= 8
                elif bikemode == cf["mt"]: base_weight *= 16
                elif bikemode == cf["ht"]: base_weight *= 32
                elif bikemode == cf["ca"]: base_weight *= 64
                elif bikemode in (cf["xx"], cf["pb"]):
                    # Penalize xx based on traffic (est. from st. type)
                    # Non-network path is rated same as a lt bl
                    if code in (3200, 3230, 3240, 3250): base_weight *= 4
                    else:
                        base_weight *= 32
                        if code in (1500, 1521):       base_weight *= 1   #lt
                        elif code == 1450:             base_weight *= 2   #mt
                        elif code == 1400:             base_weight *= 4   #ht
                        elif code == 1300:             base_weight *= 8   #ca
                        elif 1200 <= code < 1300:      base_weight *= 16  #ca+
                        elif 1100 <= code < 1200:      base_weight *= 32  #ca++
                        else:                          base_weight *= 64  #?
                elif bikemode in (cf["pm"], cf["up"]): base_weight *= 5120
                break
        
        try: last_edge = G_edges[E[-1]]
        except IndexError: pass
        else:
            # Penalize the edge if it has a different street name from the
            # previous edge
            stid_idx = self.indices["stid"] 
            stid = edge[stid_idx]
            last_stid = last_edge[stid_idx]
            if stid != last_stid: base_weight *= 1.025

        return base_weight


