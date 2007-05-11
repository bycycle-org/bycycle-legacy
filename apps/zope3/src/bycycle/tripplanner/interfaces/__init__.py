__docformat__ = "reStructuredText"

from zope.interface import Interface
from zope.schema import TextLine, Text, URI, Object


class IRegionContainer(Interface):
    pass


class IRegion(Interface):
    """A geographic region."""

    title = TextLine(
        title=u'Title',
        description=u'Region title.',
        required=True)
    
    key = TextLine(
        title=u'Key',
        description=u'Unique text ID for this region.',
        required=True)


class IAd(Interface):
    """An ad for a region."""
    
    title = TextLine(
        title=u'Title',
        description=u'Ad title.',
        required=True)
    
    content = Text(
        title=u'Text',
        description=u'Ad content.',
        required=True)

    href = URI(
        title=u'href',
        description=u'Ad URL.',
        required=True)
        
    region = Object(
        title=u'Region',
        description=u'Region this ad belongs to.',
        required=True,
        schema=IRegion)
    