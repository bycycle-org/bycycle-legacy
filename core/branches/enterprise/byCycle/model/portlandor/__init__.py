###############################################################################
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
###############################################################################
"""This module defines the Portland, OR, region."""
import math
from byCycle.model import region


block_length = 5280.0 / 20.0
jog_length = block_length / 2.0


class _Region(region.Region):
    """A factory (?) for creating Portland, OR, `Region`s."""

    title = 'Portland, OR'
    block_length = block_length
    jog_length = jog_length
    edge_attrs = ['street_name_id', 'code', 'bikemode', 'up_frac', 'abs_slp',
                  'node_f_id', 'cpd']

    def __init__(self):
        region.Region.__init__(self, 'portlandor')

    def _adjustRowForMatrix(self, row):
        adjustments = {
            'abs_slp': self.encodeFloat(row['abs_slp']),
            'up_frac': self.encodeFloat(row['up_frac']),
        }
        return adjustments


__region = None


def Region(*args, **kwargs):
    global __region
    if __region is None:
        __region = _Region(*args, **kwargs)
    return __region
