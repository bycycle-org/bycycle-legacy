from byCycle.lib import gis


class Segment(object):
    """Representation of a segment."""
    def __init__(self, data={}):
        self.__dict__.update(data)


    def getAttrsOnNumSide(self, num):
        """Get attributes for side of segment num is on.

        Get all the attributes from the segment object s that end in 'l'
        or 'r', depending on whether num is on the right or left side of s.

        Args:
        s -- a segment object
        num -- a street number (hopefully it's actually within the segment)

        Return:
        A dict of the attributes, with the 'l' or 'r' stripped off the keys

        """
        num = int(num)
        numl = int(self.fraddl) or int(self.toaddl)
        numr = int(self.fraddr) or int(self.toaddr)
        if num % 2 == numl % 2: side = 'left'
        elif num % 2 == numr % 2: side = 'right'
        return self.getAttrsOnSide(side)


    def getAttrsOnSide(self, side='left'):
        """Get attributes on side. Also get attrs that aren't side-specific.

        Return a dict of the attributes. The side-specific attrs will have
        their last char (l or r) stripped off.

        """
        if side.strip().lower() in ('left', 'l'):
            char = 'l'
            opp_char = 'r'
        elif side.strip().lower() in ('right', 'r'):
            char = 'r'
            opp_char = 'l'
        else: return None
        A = {}
        attrs = self.__dict__
        for attr in attrs:
            if attr[-1] == char: A[attr[:-1]] = attrs[attr]
            elif attr[-1] != opp_char: A[attr] = attrs[attr]
        return A


    def getIDOfSharedIntersection(self, other_segment):
        if self.fnode in (other_segment.fnode, other_segment.tnode):
            nid = self.fnode
        elif self.tnode in (other_segment.fnode, other_segment.tnode):
            nid = self.tnode
        return nid

                    
    def splitAtNum(self, num):
        """Split the segment at num. Return two new segments.

        The first seg is fnode-->num; the second is num-->fnode
        
        """
        num = int(num)
        sls = self.linestring
        sls_len = len(sls)

        fal, far = self.fraddl, self.fraddr
        tal, tar = self.toaddl, self.toaddr

        min_add = min([a for a in (fal, far, tal, tar) if a])
        max_add = max([a for a in (fal, far, tal, tar) if a])

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

        # Give s attributes of original from fnode-->num
        # Give t attributes of original from num-->tnode
        # linestring
        for i in range(ll_idx): s.linestring.append(sls[i])
        s.linestring.append(ll)
        t.linestring.append(ll)        
        for i in range(ll_idx, sls_len): t.linestring.append(sls[i])
        # weight (length)
        s.getWeight(True)
        t.getWeight(True)
        # address range
        s.toaddrl = s.toaddr = num
        t.fraddrl = t.fraddr = num
        # fake node ID
        s.tnode, t.fnode = -1, -1
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
