# Milwaukee, WI Data Mode
# 11/07/2005

from byCycle.tripplanner.model import mode
 

class Mode(mode.Mode):
    def __init__(self):
        self.region = 'milwaukeewi'
        self.edge_attrs = ['bikemode', 'lanes', 'adt', 'spd']
        mode.Mode.__init__(self)
        

if __name__ == '__main__':
    md = Mode();
    G = md.createAdjacencyMatrix()
