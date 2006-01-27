# Milwaukee Bicycle Travel Mode
# 11/07/2005

from byCycle.tripplanner.model import milwaukeewi

class Mode(milwaukeewi.Mode):
    def __init__(self):
        self.tmode = "bicycle"
        milwaukeewi.Mode.__init__(self)
        self.mph = 10

    def getEdgeWeight(self, v, edge_attrs, prev_edge_attrs):
        """Calculate weight for edge given it & last crossed edge's attrs."""
        indices = self.indices
        length = edge_attrs[indices["length"]] / 1000000.0

        cfcc = edge_attrs[indices["cfcc"]]
        try:
            cl, cat, ma, mi = cfcc[0], int(cfcc[1:]), int(cfcc[1]), int(cfcc[2])
        except (IndexError, TypeError):
            # Empty CFCC field in DB
            cl, cat, ma, mi = 'x', 0, 0, 0
            
        bikemode = edge_attrs[indices["bikemode"]]
        lanes = edge_attrs[indices["lanes"]]
        adt = edge_attrs[indices["adt"]]
        spd = edge_attrs[indices["spd"]]
        ix_sn = edge_attrs[indices["streetname_id"]]

        hours = length / self.mph

        if bikemode:
            # Adjust for network
            if   bikemode == 'l': pass
            elif bikemode == 't': hours *= 1.10
            elif bikemode == 'r': hours *= 1.30
            elif bikemode == 'p': hours *= 1.50
        else:
            # Penalize for not being on bike network
            hours *= 2.00
            # Adjust for traffic
            adt_factor = (adt * .001)
            if adt_factor < 1: adt_factor = 1
            if   40 <= cat < 50 or cat in (71, 73, 74): cfcc_factor = 1.00 #lt
            elif 30 <= cat < 40 or cat == 62: cfcc_factor = 2.00 #mt
            elif 20 <= cat < 30 or cat == 64: cfcc_factor = 4.00 #ht
            elif 10 <= cat < 20 or cat == 63: cfcc_factor = 1000 #ca
            try:
                hours *= ((adt_factor + cfcc_factor) / 2.0)
            except NameError:
                hours *= adt_factor
            # Adjust for number of lanes
            lanes_factor = lanes / 2.0
            if lanes_factor < 1: lanes_factor = 1
            hours *= lanes_factor
            
            try:
                # Penalize edge if it has different street name from previous edge
                prev_ix_sn = prev_edge_attrs[indices["streetname_id"]]
                if ix_sn != prev_ix_sn: hours += .0055555555555555
            except TypeError:
                pass
        
        return hours
