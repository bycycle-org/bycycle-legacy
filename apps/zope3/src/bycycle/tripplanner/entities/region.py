from zope.interface import implements
from zope.app.container.btree import BTreeContainer
from zope.app.container.contained import Contained
from persistent import Persistent
from bycycle.tripplanner.interfaces import IRegion, IRegionContained, IRegionContainer


class Region(Persistent):
    implements(IRegion, IRegionContained)
    title = u'Region'
    key = u'region'
    srid = 4326
    units = u'dd'
    earth_circumference = 1000
    block_length = 260
    jog_length = 130
    required_edge_attrs = [
        u'length',
        u'street_name_id',
        u'node_f_id',
        u'code',
        u'bikemode'
    ]
    edge_attrs = []
    ads = []
    __parent__ = None
    __name__ = None


class RegionContainer(BTreeContainer):
    implements(IRegionContainer)

