"""$Id$

Description goes here.

Copyright (C) 2006 Wyatt Baldwin, byCycle.org <wyatt@bycycle.org>

All rights reserved.

TERMS AND CONDITIONS FOR USE, MODIFICATION, DISTRIBUTION

1. The software may be used and modified by individuals for noncommercial, 
private use.

2. The software may not be used for any commercial purpose.

3. The software may not be made available as a service to the public or within 
any organization.

4. The software may not be redistributed.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND 
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED 
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE 
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR 
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES 
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; 
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON 
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT 
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS 
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

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
        self.xy = None
        self.address = ""
        self.hood = ""
        if data: self.init(data)

    def init(self, data):
        if "id"        in data: self.id       = int(data["id"])
        if "tzid"      in data: self.conn     = data["tzid"]
        if "category"  in data: self.category = data["category"]
        if "name"      in data: self.name     = data["name"]
        if "street_id" in data: self.street_name = data["street_id"]
        if "xy"   in data: self.xy  = gis.Point(data["xy"])
        if "address"   in data: self.address  = data["address"]
        if "hood"      in data: self.hood     = data["hood"]

    def __str__(self): return ""
