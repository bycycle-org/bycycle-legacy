###########################################################################
# $Id$
# Created 2005-11-07
#
# Portland, OR, region.
#
# Copyright (C) 2006 Wyatt Baldwin, byCycle.org <wyatt@bycycle.org>.
# All rights reserved.
# 
# For terms of use and warranty details, please see the LICENSE file included
# in the top level of this distribution. This software is provided AS IS with
# NO WARRANTY OF ANY KIND.


"""This module defines the Portland, OR, region."""
import math
from byCycle.model import region


SRID = 2913
units = 'feet'
earth_circumference = 131484672
block_length = 5280.0 / 20.0
jog_length = block_length / 2.0


class Region(region.Region):
    """A factory (?) for creating Portland, OR, `Region`s."""

    def __init__(self):
        name = 'Portland, OR'
        self.block_length = block_length
        self.jog_length = jog_length
        edge_attrs = ['street_name_id', 'code', 'bikemode', 'up_frac', 
                        'abs_slp', 'node_f_id', 'cpd']
        region.Region.__init__(self, name, SRID, units, earth_circumference,
                               edge_attrs=edge_attrs)

    def _adjustRowForMatrix(self, dbh, row):
        adjustments = {
            'abs_slp': dbh.encodeFloat(row['abs_slp']),
            'up_frac': dbh.encodeFloat(row['up_frac']),
        }
        return adjustments
        

    