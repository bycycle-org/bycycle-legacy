###########################################################################
# $Id$
# Created ???.
#
# Segment.
#
# Copyright (C) 2006 Wyatt Baldwin, byCycle.org <wyatt@bycycle.org>.
# All rights reserved.
#
# For terms of use and warranty details, please see the LICENSE file included
# in the top level of this distribution. This software is provided AS IS with
# NO WARRANTY OF ANY KIND.


class Segment(object):
    """Representation of a segment."""
    def __init__(self, data={}):
        self.__dict__.update(data)

    def getAttrsOnNumSide(self, num):
        """Get attributes for side of edge ``num`` is on.

        Get all left or right side attributes, depending on whether ``num`` is
        on the right or left side of this `Edge`.

        ``num`` `int`
            A edge number within this `Edge`

        return `dict`
            The attributes, with the 'l' or 'r' stripped from the keys

        """
        # Is the left or right side of this edge the even side?
        odd_side = ('l', 'r')[self.even_side == 'l']
        # Is ``num`` on the even or odd side of this edge?
        side = (odd_side, self.even_side)[int(num) % 2 == 0]
        # Get attributes for the side ``num`` is on
        return self.getAttrsOnSide(side)

    def getAttrsOnSide(self, side='left'):
        """Get attributes on ``side`` and attrs that aren't side-specific.

        ``side``
            Side to get attrs from (one of left, l, right, r). Side specific
            attrs look like "attr_l" or "attr_l_id".

        return `dict`
            The attributes. The side-specific attrs will have _l/_r removed
            from their keys. If an attr happens to end with an _, it will be
            stripped off.

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

