from copy import deepcopy
from byCycle.lib import gis
from byCycle.tripplanner.model import address

    
class Geocode(object):
    def __str__(self):
        return str(self.address)
    
class AddressGeocode(Geocode):
    def __init__(self, address=None, segment=None, xy=None):
        self.address = address
        self.segment = segment
        self.xy = xy
        
    def __repr__(self):
        result = {'type': 'address',
                  'number': self.address.number,
                  'street': self.address.street,
                  'place': self.address.place,
                  'x': '%.6f' % self.xy.x,
                  'y': '%.6f' % self.xy.y,
                  'e': self.segment.rowid}
        return repr(result)
    
class IntersectionGeocode(Geocode):
    def __init__(self, address=None, intersection=None):
        self.address = address
        self.intersection = intersection
        self.xy = intersection.lon_lat

    def __repr__(self):
        result = {'type': 'intersection',
                  'street1': self.address.street1,
                  'street2': self.address.street2,
                  'place1': self.address.place1,
                  'place2': self.address.place2,
                  'x': '%.6f' % self.xy.x,
                  'y': '%.6f' % self.xy.y,
                  'v': self.intersection.nid}
        return repr(result)


def geocode(inaddr, mode):
    """Choose the geocoding function based on the type of the input address.

    Call the appropriate geocoding function. Return a list of Geocode objects.

    """ 
    func = None

    try: int(inaddr)
    except ValueError: pass
    else: func = getPointGeocodes
        
    try: address.IntersectionAddress.getCrossStreets(inaddr)
    except ValueError: pass
    else: func = getIntersectionGeocodes
    
    try: address.PointAddress.getXY(inaddr)
    except ValueError: pass
    else: func = getPointGeocodes

    if not func: func = getAddressGeocodes #default
    try: geocodes = func(inaddr, mode) 
    except address.AddressNotFoundError: return []
    else: return geocodes #list of geocode objects


# Each get*Geocode returns a list of possible geocodes for the input address

def getAddressGeocodes(inaddr, mode):
    addr = address.AddressAddress(inaddr, mode)
    street = addr.street
    place = addr.place

    # Create the WHERE clause
    where = []
    where.append('%s BETWEEN MIN(fraddl,fraddr,toaddl,toaddr)' % addr.number)
    where.append('MAX(fraddl,fraddr,toaddl,toaddr)')
    where += _getPlaceWhere(place)
    stnameids = ','.join([str(i) for i in street.getIds(mode)])
    where.append('stnameid IN (%s)' % stnameids)
    where = ' AND '.join(where)

    # Get segments matching inaddr
    Q = 'SELECT rowid FROM %s WHERE %s' % (mode.tables['edges'], where)
    mode.execute(Q)
    rows = mode.fetchAll()
    if rows: rowids = [r[0] for r in rows]
    else: return []
    segs = mode.getSegmentsById(rowids)

    # Make list of geocodes for segments matching inaddr
    geocodes = []
    for s in segs:
        s_addr = deepcopy(addr)
        attrs = s.getAttrsOnNumSide(addr.number)
        for attr in ('prefix', 'name', 'type', 'suffix'):
            s_addr.street.__dict__[attr] = attrs[attr]
        for attr in ('city', 'statecode', 'zip'):
            s_addr.place.__dict__[attr] = attrs[attr]
        xy = gis.getInterpolatedXY(s.linestring,
                                   max(s.toaddl, s.toaddr) -
                                   min(s.fraddl, s.fraddr),
                                   int(addr.number) -
                                   min(s.fraddl, s.fraddr))
        code = AddressGeocode(s_addr, s, xy)
        geocodes.append(code)
    return geocodes

    
def getIntersectionGeocodes(inaddr, mode):        
    addr = address.IntersectionAddress(inaddr, mode)
    street1, street2 = addr.street1, addr.street2
    place1, place2 = addr.place1, addr.place2
    stnameids_a = ','.join([str(i) for i in street1.getIds(mode)])
    stnameids_b = ','.join([str(i) for i in street2.getIds(mode)])
    # Create the WHERE clause
    Q = 'SELECT rowid, fnode, tnode FROM %s WHERE' % mode.tables['edges']
    first = True
    for place, ids in ((place1, stnameids_a), (place2,  stnameids_b)):
        where = _getPlaceWhere(place)
        where.append('stnameid IN (%s)' % ids)
        where = ' AND '.join(where)
        mode.executeDict('%s %s' % (Q, where))
        rows = mode.fetchAllDict()
        if not rows: return []
        if first:
            first = False
            rows_a = rows
        else:
            rows_b = rows
    return _nodeCommon(addr, mode, rows_a, rows_b)

    
def getPointGeocodes(inaddr, mode):
    try:
        # Special case of node ID supplied directly
        min_nid = int(inaddr)
        addr = address.PointAddress('(0,0)', mode)
    except ValueError:
        addr = address.PointAddress(inaddr, mode)
        x, y = addr.x, addr.y
        min_nid = None
        min_dist = 2000000000
        Q = 'SELECT nid, wkt_geometry FROM %s' % (mode.tables['vertices'])
        mode.execute(Q)
        row = mode.fetchRow()
        distFunc = gis.getDistanceBetweenTwoPointsOnEarth
        while row:
            nid = row[0]
            point = gis.importWktGeometry(row[1])
            dist = distFunc(lon_a=x, lat_a=y,
                            lon_b=point.x, lat_b=point.y)
            if dist < min_dist:
                min_nid = nid
                min_dist = dist
                if min_dist < .025: break  # close enough
            row = mode.fetchRow()

        if min_nid is None: return []

    # Get segments that have our min_nid as their f or tnode
    Q = 'SELECT rowid, fnode, tnode, stnameid FROM %s ' \
        'WHERE fnode=%s OR tnode=%s' % (mode.tables['edges'], min_nid, min_nid)
    mode.executeDict(Q)
    rows = mode.fetchAllDict()

    # Index rows by street name ID
    st_rows = {}
    for row in rows:
        stnameid = row['stnameid']
        if stnameid in st_rows: st_rows[stnameid].append(row)
        else: st_rows[stnameid] = [row]

    rows_a = st_rows.popitem()[1]
    try:
        rows_b = st_rows.popitem()[1]
    except KeyError:
        rows_b = []
    return _nodeCommon(addr, mode, rows_a, rows_b)


def _nodeCommon(addr, mode, rows_a, rows_b):
    # Index all segments by their fr/tnodes
    ia, ib = {}, {}
    for i, R in ((ia, rows_a), (ib, rows_b)):
        for r in R:
            rowid, fnode, tnode = r['rowid'], r['fnode'], r['tnode']
            if fnode in i: i[fnode].append(rowid)
            else: i[fnode] = [rowid]
            if tnode in i: i[tnode].append(rowid)
            else: i[tnode] = [rowid]

    # Get IDs of segs with matching nid
    rowids, pairs = {}, []
    for nid in ia:
        if nid in ib:
            rowid_a, rowid_b = ia[nid][0], ib[nid][0]
            rowids[rowid_a], rowids[rowid_b] = 1, 1
            pairs.append((rowid_a, rowid_b))

    # Get all the segs and map them by their IDs
    S = mode.getSegmentsById(rowids.keys())
    s_dict = {}
    for s in S: s_dict[s.rowid] = s

    # Get the address and shared NID of each cross street pair
    addrs = []
    nids = []
    for p in pairs:
        s, t = s_dict[p[0]], s_dict[p[1]]
        i_addr = deepcopy(addr)
        _setStreetAndPlaceFromSegment(i_addr.street1, i_addr.place1, s)
        _setStreetAndPlaceFromSegment(i_addr.street2, i_addr.place2, t)
        addrs.append(i_addr)
        nids.append(s.getIDOfSharedIntersection(t))

    # Get all the ints and map them by their IDs
    I = mode.getIntersectionsById(nids)
    i_dict = {}
    for i in I: i_dict[i.nid] = i

    # Make a list of all the matching addresses and return it
    geocodes = []
    for addr, nid in zip(addrs, nids):
        code = IntersectionGeocode(addr, i_dict[nid])
        geocodes.append(code)
    return geocodes


## Helper functions

def _setStreetAndPlaceFromSegment(street, place, seg):
    attrs = seg.getAttrsOnSide('left')
    for attr in ('prefix', 'name', 'type', 'suffix'):
        street.__dict__[attr] = attrs[attr]
    for attr in ('city', 'statecode', 'zip'):
        place.__dict__[attr] = attrs[attr]


def _getPlaceWhere(place):
    where = []
    if place.cityid:
        cid = place.cityid
        where.append('(cityidl=%s OR cityidr=%s)' % (cid, cid))
    if place.statecode:
        sc = place.statecode
        where.append('(statecodel="%s" OR statecoder="%s")' % (sc, sc))
    if place.zip:
        z = place.zip
        where.append('(zipl=%s OR zipr=%s)' % (z, z))    
    return where
