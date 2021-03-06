###############################################################################
# $Id: identify.py 335 2006-11-16 01:39:00Z bycycle $
# Created 2006-11-16.
#
# Identify service.
#
# Copyright (C) 2006 Wyatt Baldwin, byCycle.org <wyatt@bycycle.org>.
# All rights reserved.
#
# For terms of use and warranty details, please see the LICENSE file included
# in the top level of this distribution. This software is provided AS IS with
# NO WARRANTY OF ANY KIND.
################################################################################
"""In a region and layer within that region, find feature nearest point.

Given a region (i.e., data source), a layer within that region, and a point, find the feature nearest the point and return an object representing that feature.

"""
from sqlalchemy.sql import select, func
from sqlalchemy.exceptions import InvalidRequestError
from byCycle.model import db
from byCycle.model.point import Point
from byCycle import services
from byCycle.services.exceptions import IdentifyError


class Service(services.Service):
    """Identify Service."""

    name = 'identify'

    def __init__(self, region=None):
        services.Service.__init__(self, region=region)

    def query(self, q, layer=None, input_srid=4326):
        """Find feature in layer closest to point represented by ``q``.

        ``q``
            A Point object or a string representing a point.
            
        ``layer``
            The layer to search
            
        ``input_srid``
            The SRID of the input point represented by ``q``

        return
            A domain object representing the feature nearest to ``q``.

        raise ValueError
            ``q`` can't be parsed as valid point.

        """
        try:
            point = Point(q)
        except ValueError:
            raise IdentifyError('Cannot identify because POINT is not valid: '
                                '%s.' % q)
        region = self.region
        earth_circumference = region.earth_circumference
        Entity = getattr(region.module, layer)
        c = Entity.c
        wkt = str(point)
        # Function to convert the input point to native geometry
        transform = func.transform(func.GeomFromText(wkt, input_srid),
                                   region.srid)
        # Function to get the distance between input point and table points
        distance = func.distance(transform, c.geom)
        # This is what we're SELECTing--all columns in the layer plus the
        # distance from the input point to points in the nodes table (along
        # with the node ID and geom).
        cols = c + [distance.label('distance')]
        # Limit the search to within `expand_dist` feet of the input point.
        # Keep trying until we find a match or until `expand_dist` is
        # larger than half the circumference of the earth.
        expand_dist = region.block_length
        overlaps = c.geom.op('&&')  # geometry A overlaps geom B operator
        expand = func.expand  # geometry bounds expanding function
        while expand_dist < earth_circumference:
            where = overlaps(expand(transform, expand_dist))
            sel = select(cols, where, order_by=['distance'], limit=1)
            try:
                object = Entity.selectone(sel)
            except InvalidRequestError:
                expand_dist *= 2
            else:
                return object
        raise IdentifyError('Could not identify feature nearest to "%s" in '
                            'region "%s", layer "%s"' % (q, region, layer))
