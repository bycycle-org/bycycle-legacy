################################################################################
# $Id: geocode.py 212 2006-09-11 04:16:40Z bycycle $
# Created 2006-09-25.
#
# Route classes.
#
# Copyright (C) 2006 Wyatt Baldwin, byCycle.org <wyatt@bycycle.org>.
# All rights reserved.
#
# For terms of use and warranty details, please see the LICENSE file included
# in the top level of this distribution. This software is provided AS IS with
# NO WARRANTY OF ANY KIND.
################################################################################
"""Route classes."""


###########################################################################
class Route(object):
    """Represents a route between two addresses."""

    #----------------------------------------------------------------------
    def __init__(self,
                 region,
                 start, end,
                 nodes, edges,
                 directions, linestring, distance):
        self.region = region
        self.start = start
        self.end = end
        self.nodes = nodes
        self.edges = edges
        self.directions = directions
        self.linestring = linestring
        self.distance = distance

    #----------------------------------------------------------------------
    def __repr__(self):
        route = {
            'start': self.start,
            'end': self.end,
            'linestring': repr(self.linestring),
            'directions': self.directions,
            'distance': self.distance
        }
        return repr(route)

    #----------------------------------------------------------------------
    def __str__(self):
        directions = []
        for d in self.directions:
            dbm = d['bikemode']
            bm = [', '.join([[b, '-'][b is 'n'] for b in dbm]), ''][not dbm]
            directions.append('%s on %s toward %s -- %s %s [%s]' % (
                d['turn'],
                d['street'],
                d['toward'],
                '%.2f' % (d['distance'][self.region.units]),
                self.region.units,
                bm,
            ))
        directions = '\n'.join([
            '%s%s. %s' % (['', ' '][i<10], i, d)
            for i, d
            in enumerate(directions)
        ])
        s = [
            self.start['geocode'],
            self.end['geocode'],
            'Distance: %.2f' % (self.distance[self.region.units]),
            directions,
        ]
        return '\n'.join([str(a) for a in s])
