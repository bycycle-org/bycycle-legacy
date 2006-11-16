################################################################################
# $Id$
# Created 2006-09-19.
#
# byCycle Services Package.
#
# Copyright (C) 2006 Wyatt Baldwin, byCycle.org <wyatt@bycycle.org>.
# All rights reserved.
#
# For terms of use and warranty details, please see the LICENSE file included
# in the top level of this distribution. This software is provided AS IS with
# NO WARRANTY OF ANY KIND.
################################################################################
"""Provides a base class for the byCycle core services."""
from byCycle.model import regions


class Service(object):
    """Base class for byCycle services."""

    def __init__(self, region=None):
        """Connect to database, iff not alreay connected.

        ``region`` `Region` | `string` | `None`
            Either a region key or a `Region` object. In the first case a new
            `Region` will be instantiated to geocode the address; in the
            second, the object will be used directly. ``region`` need not be
            specified; if it isn't, a specific service can try to guess it
            (most likely via the Address Normalization service).

        raise `ValueError`
            ``region`` is not a `Region` instance, a known region key or
            alias, or None.

        """
        self.region = region

    def _get_region(self):
        try:
            return self._region
        except AttributeError:
            return None
    def _set_region(self, region):
        """Set `region` to ``region``

        ``region`` `Region` | `str` | `None` -- See __init__ for details.

        """
        self._region = regions.getRegion(region)
    region = property(_get_region, _set_region)

    def query(self, q):
        """Query this service and return an object.

        ``q`` `object` -- The query object (string, list, etc)

        return `object`

        """
        raise NotImplementedError
