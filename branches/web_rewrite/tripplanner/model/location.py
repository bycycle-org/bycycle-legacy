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

import gis

class Location(object):

    def __init__(self, data=None):
        """Representation of a location.

        data -- a dict of {field (or column) name => value}

        """
        self.id = -1
        self.tzid = 0
        self.category = ""
        self.name = "" 
        self.street_id = ""
        self.lon_lat = None
        self.address = ""
        self.hood = ""
        if data: self.init(data)

    def init(self, data):
        if "id"        in data: self.id       = int(data["id"])
        if "tzid"      in data: self.conn     = data["tzid"]
        if "category"  in data: self.category = data["category"]
        if "name"      in data: self.name     = data["name"]
        if "street_id" in data: self.street_name = data["street_id"]
        if "lon_lat"   in data: self.lon_lat  = gis.Point(data["lon_lat"])
        if "address"   in data: self.address  = data["address"]
        if "hood"      in data: self.hood     = data["hood"]

    def __str__(self): return ""
