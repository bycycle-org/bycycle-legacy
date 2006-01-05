# Milwaukee Bicycle Travel Mode
# 11/07/2005

from byCycle.tripplanner.model import milwaukee

class Mode(milwaukee.Mode):
    def __init__(self):
        self.tmode = "bicycle"
        milwaukee.Mode.__init__(self)
        self.mph = 10

    def getEdgeWeight(self, edge_attrs, prev_edge_attrs):
        """Calculate a weight for the edge with ID e."""
        indices = self.indices
        length = edge_attrs[indices["length"]]
        cfcc = edge_attrs[indices["cfcc"]]
        cl, cat, ma, mi = cfcc[0], int(cfcc[1:]), int(cfcc[1]), int(cfcc[2])
        bikemode = edge_attrs[indices["bikemode"]]

        grade = edge_attrs[indices["grade"]]
        lanes = edge_attrs[indices["lanes"]]
        adt = edge_attrs[indices["adt"]]
        spd = edge_attrs[indices["spd"]]
        ix_sn = edge_attrs[indices["ix_streetname"]]

        sec = (length * 3600) / self.mph

        if bikemode != 'bt':
            # Penalize for traffic
            adt_factor = (adt * .001)
            if adt_factor < 1: adt_factor = 1
            sec *= adt_factor
            if 40 <= cat < 50 or cat == 74:   pass        #lt
            elif 30 <= cat < 40 or cat == 62: sec *= 1.25 #mt
            elif 20 <= cat < 30 or cat == 64: sec *= 1.50 #ht
            elif 10 <= cat < 20 or cat == 63: sec *= 1000 #ca
            lanes_factor = lanes / 2
            if lanes_factor < 1: lanes_factor = 1
            sec *= lanes_factor

        if bikemode:
            # Reward for being on network
            if bikemode in ('bl', 'bt'): sec *= .50
            elif bikemode == 'br':       sec *= .70
            elif bikemode == 'ps':       sec *= .90
            
        if prev_edge_attrs is not None:
            # Penalize edge if it has different street name from previous edge
            prev_ix_sn = prev_edge_attrs[indices["ix_streetname"]]
            if ix_sn != prev_ix_sn: sec += 20
        
        return sec
