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
from byCycle.util import gis


class Segment(object):
    """Representation of a segment."""
    def __init__(self, data={}):
        self.__dict__.update(data)


    def getAttrsOnNumSide(self, num):
        """Get attributes for side of segment num is on.

        Get all the attributes from this segment that end in 'l' or 'r',
        depending on whether num is on the right or left side of s.

        Args:
        num -- a street number (hopefully it's actually within the segment)

        Return:
        A dict of the attributes, with the 'l' or 'r' stripped off the keys

        """
        odd_side = ('l', 'r')[self.even_side == 'l']
        side = (odd_side, self.even_side)[int(num) % 2 == 0]
        return self.getAttrsOnSide(side)


    def getAttrsOnSide(self, side='left'):
        """Get attributes on side. Also get attrs that aren't side-specific.

        Return a dict of the attributes. The side-specific attrs will have
        their last char (l or r) stripped off. If the attr then ends with '_',
        that will be stripped off too.

        """
        if side.strip().lower() in ('left', 'l'):
            char = 'l'
            opp_char = 'r'
        elif side.strip().lower() in ('right', 'r'):
            char = 'r'
            opp_char = 'l'
        A = {}
        attrs = self.__dict__
        for attr in attrs:
            words = attr.split('_')
            if words[-1] == 'id':
                try:
                    suffix = words[-2]
                    del words[-2]
                except IndexError:
                    suffix = ''
            else:
                suffix = words[-1]
                del words[-1]
                
            # Side-specific attr
            if suffix == char:
                key = '_'.join(words)
                if key[-1] == '_':
                    key = key[:-1]
                A[key] = attrs[attr]
                
            # Non side-specific attr
            elif suffix != opp_char:
                A[attr] = attrs[attr]
        return A


    def getIDOfSharedIntersection(self, other_segment):
        try:
            if self.node_f_id in (other_segment.node_f_id,
                                  other_segment.node_t_id):
                node_id = self.node_f_id
            elif self.node_t_id in (other_segment.node_f_id,
                                    other_segment.node_t_id):
                node_id = self.node_t_id
        except AttributeError:
            return 0
        return node_id

                    
    def splitAtNum(self, num, fnid=-1, ntid=-2, nid=-1):
        """Split the segment at num. Return two new segments.

        The first seg is node_f_id-->num; the second is num-->node_f_id

        @param num The address number to split the segment at
        @param fnid An optional segment ID for the segment from=>split
        @param ntid An optional segment ID for the segment split=>to
        @param nid An optional shared node ID for the split
        @return s, t The from=>split and split=>to segments
        
        """
        num = int(num)
        sls = self.linestring
        sls_len = len(sls)

        fa, ta = int(self.addr_f), int(self.addr_t)

        try:
            min_add = min(fa, ta)
        except ValueError:
            min_add = 0
            
        try:
            max_add = max(fa, ta)
        except ValueError:
            max_add = 0
            
        seg_len = (max_add - min_add + 1) * 1.0
        pct_from_start = (num - min_add) / seg_len
        pct_from_end = 1.0 - pct_from_start

        s, t = self.clone(), self.clone()

        if sls_len == 2:
            fll, tll = sls[0], sls[-1]
            ll = (fll.x * pct_from_end + tll.x * pct_from_start,
                  fll.y * pct_from_end + tll.y * pct_from_start)
            ll_idx = 1
        else:
            # TODO: don't assume all the line string piece are equal length
            pieces = sls_len - 1 * 1.0
            pct_per_piece = (seg_len / pieces) / seg_len

            try: p = pct_from_start / pct_per_piece
            except ZeroDivisionError:
                fll, tll = sls[0], sls[-1]
                ll = (fll.x * pct_from_end + tll.x * pct_from_start,
                      fll.y * pct_from_end + tll.y * pct_from_start)
                ll_idx = 1
            else:
                import math
                floor_p = int(math.floor(p))
                ceiling_p = int(math.ceil(p))
                if floor_p == ceiling_p:
                    ll = sls[floor_p]
                    ll = (ll.x, ll.y)
                else:
                    ps = p - floor_p
                    pe = ceiling_p - p
                    fll, tll = sls[floor_p], sls[ceiling_p]
                    ll = (fll.x * pe + tll.x * ps,
                          fll.y * pe + tll.y * ps)
                ll_idx = floor_p + 1

        ll = gis.Point(ll)

        s.linestring, t.linestring = [], []

        # Give s attributes of original from node_f_id-->num
        # Give t attributes of original from num-->node_t_id
        # linestring
        for i in range(ll_idx): s.linestring.append(sls[i])
        s.linestring.append(ll)
        t.linestring.append(ll)        
        for i in range(ll_idx, sls_len): t.linestring.append(sls[i])
        # weight (length)
        s.getWeight(True)
        t.getWeight(True)
        # address range
        s.addr_t = num
        t.addr_f = num
        # fake segment IDs
        s.ix, t.ix = fnid, ntid
        # fake node ID
        s.node_t_id, t.node_f_id = nid, nid
        return s, t


    def getWeight(self, force=False):
        """Get the length of this segment (and cache it)."""
        try:
            self.weight
        except AttributeError:
            force = True
        if force:
            self.weight = gis.getLengthOfLineString(self.linestring)
        return self.weight

               
    def clone(self):
        from copy import deepcopy
        return deepcopy(self)


    def __str__(self):
        return ' '.join((self.prefix, self.name, self.type))