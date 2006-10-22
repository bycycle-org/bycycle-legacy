###########################################################################
#
# Created 2006-09-11
#
# Regions base.
#
# Copyright (C) 2006 Wyatt Baldwin, byCycle.org <wyatt@bycycle.org>.
# All rights reserved.
#
# For terms of use and warranty details, please see the LICENSE file included
# in the top level of this distribution. This software is provided AS IS with
# NO WARRANTY OF ANY KIND.


"""Provides the `Region` base class."""


class Region(object):
    """Base class for regions."""

    def __init__(self, name, SRID, units, earth_circumference, edge_attrs=[]):
        """

        ``name`` `string` -- The region's name. Must be City, State (e.g.,
        Portland, OR) matching region's package name. Region package names are
        the region's city and state abbreviation smooshed together and
        lowercase. (e.g., Portland, OR => portlandor).

        ``edge_attrs`` `list` -- A list of street attribute names.

        """
        self.name = name
        self.SRID = SRID
        self.units = units
        self.earth_circumference = earth_circumference

        # `key` is a unique identifier for the region, suitable for use as a
        # dictionary/hash/javascript key. It should be the same as the region's
        # package name.
        self.key = ''.join(name.strip().split()).replace(',', '').lower()

        # This region's adjacency matrix
        self.G = None

        # Create an index of adjacency matrix street attributes. In the matrix,
        # there is an ordered sequence of edge attributes for each street.
        # This index gives us a way to access the attributes by name while
        # keeping the size of the matrix smaller. We require that streets for
        # all regions have at least a length attribute.
        self.edge_attrs = ['length'] + edge_attrs
        self.edge_attrs_index = {}
        for i, attr in enumerate(self.edge_attrs):
            self.edge_attrs_index[attr] = i

    def _adjustRowForMatrix(self, dbh, row):
        """Make changes to ``row`` before adding it to the adjacency matrix."""
        pass

    def __str__(self):
        return '%s: %s' % (self.key, self.name)
