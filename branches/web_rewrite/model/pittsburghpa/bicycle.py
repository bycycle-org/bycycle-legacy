# Pittsburgh Travel Mode
# 11/07/2005

from byCycle.tripplanner.model import pittsburghpa

class Mode(pittsburghpa.Mode):
    def __init__(self, tmode='bicycle', pref='', **kwargs):
        self.tmode = "bicycle"
        pittsburghpa.Mode.__init__(self)
        self.mph = 10

    def getEdgeWeight(self, v, edge_attrs, prev_edge_attrs):
        """Calculate weight for edge given it & last crossed edge's attrs."""
        indices = self.indices
        length = edge_attrs[indices["length"]] / 1000000.0


        pqi = edge_attrs[indices["pqi"]]
        no_lanes = edge_attrs[indices["no_lanes"]]
        bikeability = edge_attrs[indices["bikeability"]]
        elevt =  edge_attrs[indices["elev_t"]]

        elevf =  edge_attrs[indices["elev_f"]]            
        slope =0


        #bikeability--default at 0
        #positive, up to 5, is better
        #negative, down to -5, is worse
        #-6 is freeway or other impossible edge.
        

        #bpType (used to set bikeability)
        #n=none, sp=street proposed, se=street existing,
        #oe=off-street existing, op=off-street proposed


        if elevt >0 and elevf > 0 and length > .00005: #length !=0:
            slope = abs(elevt -elevf)/(length * 100000.0) * 1300 #1100 #9000
            
        ix_sn = edge_attrs[indices["streetname_id"]]
        
        hours = length / self.mph

        if bikeability:
            if bikeability == 1: hours /= 1.1
            if bikeability == 2: hours /= 1.3
            if bikeability == 3: hours /= 1.5
            if bikeability == 4: hours /= 1.7
            if bikeability == 5: hours /= 1.9
            if bikeability == -1: hours *= 1.1
            if bikeability == -2: hours *= 1.3 
            if bikeability == -3: hours *= 1.5
            if bikeability == -4: hours *= 1.7
            if bikeability == -5: hours *= 1.9
            if bikeability == -6: hours *=5000 


        #pavement quality index
        if pqi > 6.5: #and pqi <=7.5:
            hours /= (pqi/6.5)
                    

        if no_lanes:
            lanes_factor = no_lanes / 2.0
            if lanes_factor>1:
                hours *= 3.0/4.0* lanes_factor

           
        if slope > 0:
            hours *= (slope + 1)


        try:
            # Penalize edge if it has different street name from previous edge
            prev_ix_sn = prev_edge_attrs[indices["streetname_id"]]
            if ix_sn != prev_ix_sn:
                hours += .0075555555555555  #.0055555555555555        
        except TypeError:
            pass

       
        return hours
