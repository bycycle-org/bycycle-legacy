# Milwaukee, WI Data Mode
# 11/07/2005

from byCycle.tripplanner.model import mode
 

class Mode(mode.Mode):
    def __init__(self):
        self.region = 'milwaukeewi'
        self.edge_attrs = ['bikemode', 'lanes', 'adt', 'spd']
        mode.Mode.__init__(self)

    def _adjustRowForMatrix(self, row):
        pass
##         one_way = row['one_way']
##         if one_way == 'ft':
##             one_way = 1
##         elif one_way == 'tf':
##             one_way = 2
##         elif one_way == '':
##             one_way = 3
##         else:
##             one_way = 0
##         row['one_way'] = one_way

if __name__ == '__main__':
    md = Mode();
    G = md.createAdjacencyMatrix()
