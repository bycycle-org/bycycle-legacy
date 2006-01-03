# Milwaukee Bicycle Travel Mode
# 11/07/2005

from byCycle.tripplanner.model import milwaukee

class Mode(milwaukee.Mode):
    def __init__(self):
        self.tmode = "bicycle"
        milwaukee.Mode.__init__(self)
        self.fps = 14.667  # 10mph

    def getEdgeWeight(self, edge_attrs, E):
        """Calculate a weight for the edge with ID e."""
        feet = edge_attrs[self.indices["feet"]]
        sec = feet / self.fps

        try:
            try:
                last_edge_attrs = E[-1]
            except KeyError:
                last_edge_attrs = E[-1]
        except IndexError:
            pass
        else:
            # Penalize edge if it has different street name from previous edge
            stid_idx = self.indices["stnameid"]
            stid = edge_attrs[stid_idx]
            prev_stid = last_edge_attrs[stid_idx]
            if stid != prev_stid: sec += 20
        
        return sec


    def _getLeastTrafficWeight(self):
        base_weight = edge_attrs[self.indices["weight"]]
        flags = edge_attrs[self.indices["flags"]]
        code = edge_attrs[self.indices["code"]]

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
        
        try: last_edge_attrs = G_edges[E[-1]]
        except IndexError: pass
        else:
            # Penalize the edge if it has a different street name from the
            # previous edge
            stid_idx = self.indices["stid"] 
            stid = edge_attrs[stid_idx]
            last_stid = last_edge_attrs[stid_idx]
            if stid != last_stid: base_weight *= 1.025

        return base_weight


