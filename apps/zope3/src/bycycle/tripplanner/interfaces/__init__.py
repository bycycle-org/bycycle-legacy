__docformat__ = "reStructuredText"

import zope.interface
import zope.schema

from zope.app.container.constraints import ContainerTypesConstraint
from zope.app.container.constraints import ItemTypePrecondition
from zope.app.container.interfaces import IContained, IContainer


class IAd(zope.interface.Interface):
    """An ad for a region."""
    
    title = zope.schema.TextLine(
        title=u'Title',
        description=u'Ad title and link text.')
    
    content = zope.schema.Text(
        title=u'Text',
        description=u'Ad content.')

    href = zope.schema.URI(
        title=u'href',
        description=u'Ad URL.')


class IRegion(zope.interface.Interface):
    """A geographic region."""

    title = zope.schema.TextLine(
        title=u'Title',
        description=u'Region title.')
    
    key = zope.schema.TextLine(
        title=u'Key',
        description=u'Unique text ID for this region.')

    srid = zope.schema.Int(
        title=u'SRID',
        description=u'Spatial reference ID')
    
    units = zope.schema.TextLine(
        title=u'Units',
        description=u'Units (feet, meters, dd, etc)')

    earth_circumference = zope.schema.Int(
        title=u'Cimcumference of the Earth',
        description=u'Cimcumference of the Earth')

    block_length = zope.schema.Int(
        title=u'Length of a Block',
        description=u'Length of a block')

    jog_length = zope.schema.Int(
        title=u'Length of a Jog',
        description=u'Length of a jog')

    required_edge_attrs = zope.schema.List(
        title=u'Required Edge Attributes',
        description=u'Edge attributes that all regions are required to have',
        value_type=zope.schema.TextLine(),
        readonly=True)

    edge_attrs = zope.schema.List(
        title=u'Additional Edge Attributes',
        description=u'Additional edge attributes that are used for routing',
        value_type=zope.schema.TextLine(),
        required=False)        

    ads = zope.schema.List(
        title=u'Ads',
        description=u'Ads',
        value_type=zope.schema.Object(schema=IAd, title=u'Ad'),
        required=False)


class IRegionContainer(IContainer):
    """Container for regions."""

    def __setitem__(name, obj):
        pass
    
    __setitem__.precondition = ItemTypePrecondition(IRegion)


class IRegionContained(IContained):

    __parent__ = zope.schema.Field(
        constraint = ContainerTypesConstraint(IRegionContainer))

