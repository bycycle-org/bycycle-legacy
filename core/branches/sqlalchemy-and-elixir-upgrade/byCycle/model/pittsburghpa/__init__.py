################################################################################
# $Id$
# Created 2005-11-07.
#
# Pittsburgh, PA,, Bicycle Travel Mode.
#
# Copyright (C) 2006 Wyatt Baldwin, byCycle.org <wyatt@bycycle.org>.
# All rights reserved.
# 
# For terms of use and warranty details, please see the LICENSE file included
# in the top level of this distribution. This software is provided AS IS with
# NO WARRANTY OF ANY KIND.
################################################################################
"""This module defines the Pittsburgh, PA, region."""
import math
from byCycle.model import region


block_length = 5280.0 / 20.0
jog_length = block_length / 2.0


class _Region(region.Region):
    """A factory (?) for creating Pittsburgh, PA, `Region`s."""

    title = 'Pittsburgh, PA'
    block_length = block_length
    jog_length = jog_length
    edge_attrs = ['pqi', 'no_lanes', 'bptype', 'bikeability', 'elev_f', 
                  'elev_t']
    
    def __init__(self):
        region.Region.__init__(self, 'pittsburghpa')
        
    def _adjustRowForMatrix(self, row):
        one_way = row['one_way']
        if one_way == 'ft':
            one_way = 1
        elif one_way == 'tf':
            one_way = 2
        elif one_way == '':
            one_way = 3
        else:
            one_way = 0
        return {'one_way': one_way}


__region = None


def Region(*args, **kwargs):
    global __region
    if __region is None:
        __region = _Region(*args, **kwargs)
    return __region
