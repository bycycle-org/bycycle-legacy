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
        #print 'edgeAttr' + str(edge_attrs)
        indices = self.indices
        length = edge_attrs[indices["length"]] / 1000000.0

       # cfcc = edge_attrs[indices["cfcc"]]
        pqi = edge_attrs[indices["pqi"]]
        no_lanes = edge_attrs[indices["no_lanes"]]
        #need sto add
       # slope = edge_attrs[indices["slope"]] * 9000.0 #???
       # byType = edge_attrs[indices["bpType"]] 
        bikeability = edge_attrs[indices["bikeability"]]
        elevt =  edge_attrs[indices["elev_t"]]

        elevf =  edge_attrs[indices["elev_f"]]            
        slope =0
        #bpType = ''
        #bikeability = 0
        #bikeability--default at 0
        #positive, up to 5, is better
        #negative, down to -5, is worse
        #-6 is freeway or other impossible edge.
        

        #bpType (used to set bikeability)
        #n=none, sp=street proposed, se=street existing,
        #oe=off-street existing, op=off-street proposed

        if elevt !=0 and elevf != 0 and length !=0:
            slope = abs(elevt -elevf)/(length * 100000.0) * 1100 #9000
        #print 'length: ' + str(length) +' pqi: ' + str(pqi) + ' no_lanes: ' + str(no_lanes)  +' bikeability: ' + str(bikeability)  +' slope: ' + str(slope)
        #try:
        
            #cl, cat, ma, mi = cfcc[0], int(cfcc[1:]), int(cfcc[1]), int(cfcc[2])
        #except (IndexError, TypeError):
            # Empty CFCC field in DB
            #cl, cat, ma, mi = 'x', 0, 0, 0
            

        ix_sn = edge_attrs[indices["streetname_id"]]

       

        hours = length / self.mph

        #if bikeability >2:
         #   hours /= (bikeability / 2.0) #means only matters for >2, <-2
           # print "positive bikeability. ix_sn: " + str(ix_sn)
           #too much
            
        #if bikeability < -2:
         #   avBikeability = 0 - bikeability
          #  hours *= (avBikeability / 2.0)
            #print 'negative bikeability'
        #if bikeability < -6:
         #   hours *= 1000

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
            if bikeability == -6: hours *=5000 #1000

            
            #if   bikemode == 'l': pass
            #elif bikemode == 't': hours *= 1.10
            #elif bikemode == 'r': hours *= 1.30
            #elif bikemode == 'p': hours *= 1.50
        

#         #nulls should be sent to 5, or -1 and avoided
#        if pqi:
#            if pqi != 0:
#                #pqi = .01
#                #need to distinguish 0 from blank
#                # blank should become 5
#                hours /= (pqi/5.0) #? # will make too low?
#        #else: hours /= (3.0/4)

        
        if pqi > 6.5: #and pqi <=7.5:
            hours /= (pqi/6.5) # too much effect?
        
            
            
            

        if no_lanes:
            lanes_factor = no_lanes / 2.0
            #hours *= lanes_factor #??? too much effect?
           #hours *= 3.0/4.0* lanes_factor
            if lanes_factor>1:
                hours *= 3.0/4.0* lanes_factor

               
           
            #FOR ADDING SLOPE. jb
        #slope = -1
        if slope > 0:
            hours *= (slope + 1) ##JUST TEST depends on units (what if 0<s<1?)

       # if bikemode:
            # Adjust for network
            #if   bikemode == 'l': pass
            #elif bikemode == 't': hours *= 1.10
            #elif bikemode == 'r': hours *= 1.30
            #elif bikemode == 'p': hours *= 1.50
       # else:
            # Penalize for not being on bike network
            #hours *= 2.00
            # Adjust for traffic
            #adt_factor = (adt * .001)
            #if adt_factor < 1: adt_factor = 1
            #if   40 <= cat < 50 or cat in (71, 73, 74): cfcc_factor = 1.00 #lt
            #elif 30 <= cat < 40 or cat == 62: cfcc_factor = 2.00 #mt
            #elif 20 <= cat < 30 or cat == 64: cfcc_factor = 4.00 #ht
            #elif 10 <= cat < 20 or cat == 63: cfcc_factor = 1000 #ca
            #try:
             #   hours *= ((adt_factor + cfcc_factor) / 2.0)
            #except NameError:
            #    hours *= adt_factor
            # Adjust for number of lanes
            #lanes_factor = lanes / 2.0
            #if lanes_factor < 1: lanes_factor = 1
            #hours *= lanes_factor
            
           # try:
                # Penalize edge if it has different street name from previous edge
           #     prev_ix_sn = prev_edge_attrs[indices["streetname_id"]]
           #     if ix_sn != prev_ix_sn: hours += .0055555555555555
           # except TypeError:
           #     pass

         #try:
                # Penalize edge if it has different street name from previous edge



      # to add: width?, lanes?, combo?, topo, pavement quality index,
      # streets on city bike plan
      # trails

        #print 'hours ' + str(hours)         

        try:
            prev_ix_sn = prev_edge_attrs[indices["streetname_id"]]
            if ix_sn != prev_ix_sn:
                hours += .0075555555555555
                #hours += .0055555555555555        
        except TypeError:
            pass

        #print 'hours ' + str(hours) + ' ixsn ' + str(ix_sn) + ' slope ' + str(slope)
       
        return hours
