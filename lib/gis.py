"""
$$$
:Author: Wyatt Baldwin
:Copyright: 2005 byCycle.org
:License: GPL
:Version: 0
:Date: 15 Aug 2005
$$$

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
ERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""

import math
from math import sin, cos, acos, atan2, radians, degrees

# Abbreviation to degree
directions_atod = {"n": 0,   "s": 180,  "e": 90,   "w": 270,
                   "ne": 45, "nw": 315, "se": 135, "sw": 225}

# Degree to abbreviation
directions_dtoa = {0:  "n",  180: "s",  90:  "e",  270: "w",
                   45: "ne", 315: "nw", 135: "se", 225: "sw"}

# Degree to type
directions_dtot = {0   : 'north',
                   180 : 'south',
                   90  : 'east',
                   270 : 'west',
                   45  : 'northeast',
                   315 : 'northwest',
                   135 : 'southeast',
                   225 : 'southwest'}

# Abbreviation to type
directions_atot = {'n'  : 'north',
                   's'  : 'south',
                   'e'  : 'east',
                   'w'  : 'west',
                   'ne' : 'northeast',
                   'nw' : 'northwest',
                   'se' : 'southeast',
                   'sw' : 'southwest'}

# Type to abbreviation
directions_ttoa = {'north'     : 'n',
                   'south'     : 's',
                   'east'      : 'e',
                   'west'      : 'w',
                   'northeast' : 'ne',
                   'northwest' : 'nw',
                   'southeast' : 'se',
                   'southwest' : 'sw'}

earth_radius = 3959
equator_circumference = 24902
miles_per_degree_at_equator = equator_circumference/360


def getDistanceBetweenTwoPointsOnEarth(lon_lat_a=None, lon_lat_b=None,
                                       lon_a=None, lat_a=None,
                                       lon_b=None, lat_b=None):
    if lon_lat_a and lon_lat_b:
        lon_a = lon_lat_a.x
        lat_a = lon_lat_a.y
        lon_b = lon_lat_b.x
        lat_b = lon_lat_b.y
    if lon_a == lon_b and lat_a == lat_b: return 0
    return earth_radius * \
           acos(cos(radians(lat_a)) * \
                cos(radians(lat_b)) * \
                cos(radians(lon_b-lon_a)) + \
                sin(radians(lat_a)) * \
                sin(radians(lat_b)))


def getLengthOfLineString(linestring,
                          distanceFunc=getDistanceBetweenTwoPointsOnEarth):
    length = 0
    for i, p in enumerate(linestring[:-1]):
        length += distanceFunc(p, linestring[i+1])
    return length


def getDistanceBetweenTwoPoints(p, q):
    x1, y1 = p.x, p.y
    x2, y2 = q.x, q.y
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    length = math.sqrt(math.pow(dx, 2) + math.pow(dy, 2))
    return length


def getDistanceBetweenTwoLatitudes(lat_a, lat_b):
    return miles_per_degree_at_equator * abs(lat_b - lat_a)


def getDistanceBetweenTwoLongitudes(lat, lon_a, lon_b):
    return cos(radians(lat)) * miles_per_degree_at_equator * abs(lon_b - lon_a)


def getBearingGivenStartAndEndPoints(p, q):
    dx = q.x - p.x
    dy = q.y - p.y
    deg = degrees(atan2(dx, dy))
    while deg < 0: deg += 360
    return deg

def getInterpolatedXY(linestring, length, distance_from_start):
    """
    linestring -- a list of Points (having x and y attributes)
    length -- the length of the linestring (in any convenient units)
    distance_from_start -- how far the point to interpolate is from the
                           start of the linestring (in same units as length)

    return -- an interpolated point
    """
    ls_len = len(linestring)

    if type(linestring) != type([]) or ls_len < 2: return None

    pct_from_start = distance_from_start / length
    pct_from_end = 1.0 - pct_from_start
    
    if ls_len == 2:
        fxy, txy = linestring[0], linestring[-1]
        lon_lat = (fxy.x * pct_from_end + txy.x * pct_from_start,
                   fxy.y * pct_from_end + txy.y * pct_from_start)
    else:
        # TODO: don't assume all the line string piece are equal length        
        pieces = ls_len - 1 * 1.0
        pct_per_piece = (length / pieces) / length

        try: p = pct_from_start / pct_per_piece
        except ZeroDivisionError:
            fxy, txy = linestring[0], linestring[-1]
            lon_lat = (fxy.x*pct_from_end + txy.x*pct_from_start,
                       fxy.y*pct_from_end + txy.y*pct_from_start)
        else:
            import math
            floor_p = int(math.floor(p))
            ceiling_p = int(math.ceil(p))
            if floor_p == ceiling_p:
                xy = linestring[floor_p]
                lon_lat = (xy.x, xy.y)
            else:
                ps = p - floor_p
                pe = ceiling_p - p
                fxy, txy = linestring[floor_p], linestring[ceiling_p]
                lon_lat = (fxy.x * pe + txy.x * ps,
                           fxy.y * pe + txy.y * ps)
                
    return Point(lon_lat)


def getInterpolatedLonLatForSegmentAddress(segment, street_number):
    s = segment
    num = int(street_number)
    sls = s.line_string
    ls_len = len(sls)

    if s.fraddl < s.toaddl:
        fradd = min(s.fraddl, s.fraddr)
        toadd = max(s.toaddl, s.toaddr)
    else: 
        fradd = min(s.toaddl, s.toaddr)
        toadd = max(s.fraddl, s.fraddr)
        
    length = toadd - fradd * 1.0
    pct_from_start = (num - fradd) / length
    pct_from_end = 1.0 - pct_from_start
    
    if ls_len == 2:
        fll, tll = sls[0], sls[-1]
        lon_lat = (fll.x * pct_from_end + tll.x * pct_from_start,
                   fll.y * pct_from_end + tll.y * pct_from_start)
    else:
        pieces = ls_len - 1 * 1.0
        pct_per_piece = (length / pieces) / length

        try: p = pct_from_start / pct_per_piece
        except ZeroDivisionError:
            fll, tll = sls[0], sls[-1]
            lon_lat = (fll.x*pct_from_end + tll.x*pct_from_start,
                       fll.y*pct_from_end + tll.y*pct_from_start)
        else:
            import math
            floor_p = int(math.floor(p))
            ceiling_p = int(math.ceil(p))
            if floor_p == ceiling_p:
                ll = sls[floor_p]
                lon_lat = (ll.x, ll.y)
            else:
                ps = p - floor_p
                pe = ceiling_p - p
                fll, tll = sls[floor_p], sls[ceiling_p]
                lon_lat = (fll.x * pe + tll.x * ps,
                           fll.y * pe + tll.y * ps)
                
    return Point(lon_lat)


def importWktGeometry(wkt_geometry):
    """Return a simple Python object for the given WKT Geometry string."""
    wkt_type, wkt_data = wkt_geometry.lower().split(' ', 1)
    wkt_data = wkt_data[1:-1]
    if wkt_type == 'linestring':
        wkt_data = wkt_data.split(',')
        wkt_data = [d.split() for d in wkt_data]
        linestring = [Point((d[0], d[1])) for d in wkt_data]
        return linestring
    elif wkt_type == 'point':
        wkt_data = wkt_data.split()[0:2]
        return Point((wkt_data[0], wkt_data[1]))
    else:
        return None

    
class Point(object):

    def __init__(self, x_y):
        """Create a new Point from the supplied 2-tuple or string.
        
        @param x_y -- either a 2-tuple of floats (or string representations of
                      floats), a string that will eval as such a tuple, or
                      another Point

        TODO: Fix this so it just accepts x and y args. Why it accepts a tuple,
        I don't know???
        
        """        
        if type(x_y) == type(self):
            # x_y is another point
            self.x, self.y = x_y.x, x_y.y
            self.xStr, self.yStr = x_y.xStr, x_y.yStr
        else:
            if type(x_y) == type((1,2)):
                # See if x_y is a 2-tuple (either of floats or string
                # reprensentations of floats)...
                self.xStr, self.yStr = str(x_y[0]), str(x_y[1])
            elif type(x_y) == type("(1,2)"):
                # See if x_y is a string that will eval as a 2-tuple
                tmp_x_y = eval(x_y)
                self.xStr, self.yStr = str(tmp_x_y[0]), str(tmp_x_y[1])    
            self.x, self.y = float(self.xStr), float(self.yStr)
            self.xStr, self.yStr = self.xStr.strip(), self.yStr.strip()

    def getX(self): return self.x
    def getY(self): return self.y
    def getXY(self): return (self.x, self.y)

    def getXStr(self): return self.xStr
    def getYStr(self): return self.yStr

    def __str__(self):  return "Point: x = %s, y = %s" % (self.x, self.y)
    def __repr__(self): return "{'x': %s, 'y': %s}" % (self.x, self.y)


if __name__ == '__main__':
    l = 'LINESTRING (1 2 3, 2 2 4, 3 2 5)'
    for p in importWktGeometry(l): print p,
    print
    p = 'POINT (1 2)'
    print importWktGeometry(p)
