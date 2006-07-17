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

class Intersection(object):
    """Representation of an intersection."""
    def __init__(self, data={}):
        cross_streets = []  # list of Street objects
        lon_lat = None      # gis.Point object
        self.__dict__.update(data)

    def __str__(self):
        return ' & '.join(['%s %s' % (str(st.number), str(st))
                            for st in self.cross_streets])
