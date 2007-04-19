###############################################################################
# $Id$
# Created 2005-11-07
#
# Milwaukee, WI, region.
#
# Copyright (C) 2006 Wyatt Baldwin, byCycle.org <wyatt@bycycle.org>.
# All rights reserved.
#
# For terms of use and warranty details, please see the LICENSE file included
# in the top level of this distribution. This software is provided AS IS with
# NO WARRANTY OF ANY KIND.
###############################################################################
"""This module defines the Milwaukee, WI, region."""
import math
from byCycle.model import region


block_length = 5280.0 / 20.0
jog_length = block_length / 2.0


class _Region(region.Region):

    title = 'Milwaukee, WI'
    block_length = block_length
    jog_length = jog_length
    edge_attrs = ['bikemode', 'lanes', 'adt', 'spd']

    def __init__(self):
        region.Region.__init__(self, 'milwaukeewi')

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
        row['one_way'] = one_way


__region = None


def Region(*args, **kwargs):
    global __region
    if __region is None:
        __region = _Region(*args, **kwargs)
    return __region
