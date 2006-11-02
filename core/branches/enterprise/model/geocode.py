###########################################################################
# $Id$
# Created 2005-??-??.
#
# Geocode classes.
#
# Copyright (C) 2006 Wyatt Baldwin, byCycle.org <wyatt@bycycle.org>.
# All rights reserved.
#
# For terms of use and warranty details, please see the LICENSE file included
# in the top level of this distribution. This software is provided AS IS with
# NO WARRANTY OF ANY KIND.


"""Geocode classes."""
from cartography.proj import SpatialReference


###########################################################################
class Geocode(object):
    """Geocode base class.

    Attributes
    ----------

    ``address`` `Address` -- The associated address
    ``network_id`` `int` -- Either a node or edge ID
    ``xy`` `Point` -- Geographic location

    """

    #----------------------------------------------------------------------
    def __init__(self, region, address, network_id, xy):
        """

        ``address`` -- `Address`
        ``network_id`` -- `Edge` or `Node` ID
        ``xy`` -- A point with x and y attributes

        """
        self.region = region
        self.address = address
        self.network_id = network_id
        xy.srs = SpatialReference(epsg=region.SRID)
        self.xy = xy
        xy_ll = xy.copy()
        ll_srs = SpatialReference(epsg=4326)
        xy_ll.transform(src_proj=str(self.xy.srs), dst_proj=str(ll_srs))
        self.xy_ll = xy_ll

    #----------------------------------------------------------------------
    def __str__(self):
        return '\n'.join((str(self.address), str(self.xy)))

    #----------------------------------------------------------------------
    def urlStr(self):
        s_addr = str(self.address).replace('\n', ', ')
        num = getattr(self.address, 'number', '')
        id_addr = ('%s %s' % (num, self.network_id)).lstrip()
        return ';'.join((s_addr, id_addr)).replace(' ', '+')

    #----------------------------------------------------------------------
    def __repr__(self):
        result = {
            'type': 'geocode',
            'street_name': self.address.street_name,
            'place': self.address.place,
            'address': str(self.address),
            'point': self.xy_ll,
            'network_id': self.network_id
        }
        return repr(result)


###########################################################################
class PostalGeocode(Geocode):
    """Represents a geocode that is associated with a postal address.

    Attributes
    ----------

    ``address`` `PostalAddress`
    ``edge`` `Edge`
    ``xy`` `Point` -- Geographic location
    ``location`` `float` -- Location in [0, 1] of point in ``edge``

    """

    #----------------------------------------------------------------------
    def __init__(self, region, address, edge):
        """

        ``address`` `PostalAddress`
        ``edge`` `Edge`

        """
        xy, location = edge.getPointAndLocationOfNumber(address.number)
        Geocode.__init__(self, region, address, edge.id, xy)
        self.location = location
        self.edge = edge

    #----------------------------------------------------------------------
    def __repr__(self):
        result = {
            'type': 'postal',
            'number': self.address.number,
            'street_name': self.address.street_name,
            'place': self.address.place,
            'address': str(self.address),
            'point': {'x': self.xy_ll.x, 'y': self.xy_ll.y},
            'network_id': self.network_id
        }
        return repr(result)

    #----------------------------------------------------------------------
    def __eq__(self, other):
        """Compare two `PostalGeocode`s for equality """
        return (
            (self.network_id == other.network_id) and
            (self.address.number == other.address.number)
        )


###########################################################################
class IntersectionGeocode(Geocode):
    """Represents a geocode that is associated with an intersection.

    Attributes
    ----------

    ``address`` `IntersectionAddress`
    ``node`` `Node`

    """

    #----------------------------------------------------------------------
    def __init__(self, region, address, node):
        """

        ``address`` -- `IntersectionAddress`
        ``node`` -- `Node`

        """
        xy = node.geom
        Geocode.__init__(self, region, address, node.id, xy)
        self.node = node

    #----------------------------------------------------------------------
    def __repr__(self):
        result = {
            'type': 'intersection',
            'street_name1': self.address.street_name1,
            'street_name2': self.address.street_name2,
            'place1': self.address.place1,
            'place2': self.address.place2,
            'address': str(self.address),
            'point': {'x': self.xy_ll.x, 'y': self.xy_ll.y},
            'network_id': self.network_id
        }
        return repr(result)

    #----------------------------------------------------------------------
    def __eq__(self, other):
        """Compare two `IntersectionGeocode`s for equality """
        return (self.network_id == other.network_id)
