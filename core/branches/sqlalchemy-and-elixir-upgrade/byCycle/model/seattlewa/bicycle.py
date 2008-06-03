###############################################################################
# $Id: bicycle.py 912 2007-05-21 03:52:46Z bycycle $
# Created 2005-11-07.
#
# Seattle, WA, Bicycle Travel Mode.
#
# Copyright (C) 2006, 2007 Wyatt Baldwin, byCycle.org <wyatt@bycycle.org>.
# All rights reserved.
# 
# For terms of use and warranty details, please see the LICENSE file included
# in the top level of this distribution. This software is provided AS IS with
# NO WARRANTY OF ANY KIND.
###############################################################################
"""Bicycle travel mode for Seattle, WA, region."""
from byCycle.model import tmode
from byCycle.model.entities.util import float_decode


class BikeDesignation:
  NOT_DESIGNATED, PATH, LANE, URBAN_CONNECTOR, NEIGHBORHOOD_CONNECTOR = range(5)


class DesignationWeightMap(dict):
  def __init__(self):
    # avoid anything without a designation
    self[ BikeDesignation.NOT_DESIGNATED ] = 2;

    # bike paths are the most preferable route
    self[ BikeDesignation.PATH ] = .75;

    # lanes are the next best thing
    self[ BikeDesignation.LANE ] = .9;

    # not sure what these will mean...
    self[ BikeDesignation.URBAN_CONNECTOR ] = 1;
    self[ BikeDesignation.NEIGHBORHOOD_CONNECTOR ] = 1;


class TravelMode(tmode.TravelMode):

    def __init__(self, region, pref=None):
        tmode.TravelMode.__init__(self)
        self.avg_mph = 10
        global indices
        indices = region.edge_attrs_index

    def getEdgeWeight(self, v, edge_attrs, prev_edge_attrs):
        """Calculate weight for edge given it & last crossed edge's attrs."""
        length = edge_attrs[indices['length']] * float_decode
        bikeclass = edge_attrs[indices['bikemode']]
        node_f_id = edge_attrs[indices['node_f_id']]
        streetname_id = edge_attrs[indices['street_name_id']]
 
        # TODO: implement slope awareness
        hours = length * self.avg_mph;

        map = DesignationWeightMap()
        hours *= map[ bikeclass ]

        # Penalize edge if it has different street name from previous edge
        try:
            prev_ix_sn = prev_edge_attrs[indices['street_name_id']]
            if streetname_id != prev_ix_sn:
                hours += .0027777  # 10 seconds
        except TypeError:
            pass        

        return hours
