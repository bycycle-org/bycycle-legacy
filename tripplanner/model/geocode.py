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
                  'e': self.segment.ix}
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
                  'v': self.intersection.id}
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
    where.append('(%s BETWEEN MIN(addr_f, addr_t) AND MAX(addr_f, addr_t))' % \
                 addr.number)
    where += _getPlaceWhere(place)
    ix_streetnames = ','.join([str(i) for i in street.getIds(mode)])
    where.append('ix_streetname IN (%s)' % ix_streetnames)
    where = ' AND '.join(where)

    # Get segments matching inaddr
    Q = 'SELECT ix FROM %s WHERE %s' % (mode.tables['edges'], where)
    mode.execute(Q)
    rows = mode.fetchAll()
    if rows: ixs = [r[0] for r in rows]
    else: return []
    segs = mode.getSegmentsById(ixs)

    # Make list of geocodes for segments matching inaddr
    geocodes = []
    for s in segs:
        s_addr = deepcopy(addr)
        attrs = s.getAttrsOnNumSide(addr.number)
        for attr in ('prefix', 'name', 'type', 'suffix'):
            s_addr.street.__dict__[attr] = attrs[attr]
        for attr in ('city', 'id_state', 'zip'):
            s_addr.place.__dict__[attr] = attrs[attr]
        xy = gis.getInterpolatedXY(s.linestring,
                                   max(s.addr_f, s.addr_t) -
                                   min(s.addr_f, s.addr_t),
                                   int(addr.number) -
                                   min(s.addr_f, s.addr_t))
        code = AddressGeocode(s_addr, s, xy)
        geocodes.append(code)
    return geocodes

    
def getIntersectionGeocodes(inaddr, mode):        
    addr = address.IntersectionAddress(inaddr, mode)
    street1, street2 = addr.street1, addr.street2
    place1, place2 = addr.place1, addr.place2
    ix_streetnames_a = ','.join([str(i) for i in street1.getIds(mode)])
    ix_streetnames_b = ','.join([str(i) for i in street2.getIds(mode)])
    # Create the WHERE clause
    Q = 'SELECT ix, id_node_f, id_node_t FROM %s WHERE' % mode.tables['edges']
    first = True
    for place, ids in ((place1, ix_streetnames_a),
                       (place2,  ix_streetnames_b)):
        where = _getPlaceWhere(place)
        where.append('ix_streetname IN (%s)' % ids)
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
        min_id = int(inaddr)
        addr = address.PointAddress('(0,0)', mode)
    except ValueError:
        addr = address.PointAddress(inaddr, mode)
        x, y = addr.x, addr.y
        min_id = None
        min_dist = 2000000000
        Q = 'SELECT id, wkt_geometry FROM %s' % (mode.tables['vertices'])
        mode.execute(Q)
        row = mode.fetchRow()
        distFunc = gis.getDistanceBetweenTwoPointsOnEarth
        while row:
            id = row[0]
            point = gis.importWktGeometry(row[1])
            dist = distFunc(lon_a=x, lat_a=y,
                            lon_b=point.x, lat_b=point.y)
            if dist < min_dist:
                min_id = id
                min_dist = dist
                if min_dist < .025: break  # close enough
            row = mode.fetchRow()

        if min_id is None: return []

    # Get segments that have our min_id as their f or id_node_t
    Q = 'SELECT ix, id_node_f, id_node_t, ix_streetname ' \
        'FROM %s ' \
        'WHERE id_node_f=%s OR id_node_t=%s' % \
        (mode.tables['edges'], min_id, min_id)
    mode.executeDict(Q)
    rows = mode.fetchAllDict()

    # Index rows by street name ID
    st_rows = {}
    for row in rows:
        ix_streetname = row['ix_streetname']
        if ix_streetname in st_rows:
            st_rows[ix_streetname].append(row)
        else:
            st_rows[ix_streetname] = [row]

    rows_a = st_rows.popitem()[1]
    try:
        rows_b = st_rows.popitem()[1]
    except KeyError:
        rows_b = []

    if rows_b:
        # Found point at intersection
        return _nodeCommon(addr, mode, rows_a, rows_b)
    else:
        # Found point at dead end
        row = rows_a[0]
        addr = address.AddressAddress('', mode)
        s = mode.getSegmentById(row['ix'])
        i = mode.getIntersectionById(min_id)
        # Set address number to num at min_nid end of segment
        if min_id == s.id_node_f:
            addr.number = s.addr_f
        else:
            addr.number = s.addr_t
        _setStreetAndPlaceFromSegment(addr.street, addr.place, s)
        code = IntersectionGeocode(addr, i)
        return [code]


def _nodeCommon(addr, mode, rows_a, rows_b):
    # Index all segments by their fr/id_node_ts
    ia, ib = {}, {}
    for i, R in ((ia, rows_a), (ib, rows_b)):
        for r in R:
            ix = r['ix']
            id_node_f, id_node_t = r['id_node_f'], r['id_node_t']
            if id_node_f in i: i[id_node_f].append(ix)
            else: i[id_node_f] = [ix]
            if id_node_t in i: i[id_node_t].append(ix)
            else: i[id_node_t] = [ix]

    # Get IDs of segs with matching id
    ixs, pairs = {}, []
    for ix in ia:
        if ix in ib:
            ix_a, ix_b = ia[ix][0], ib[ix][0]
            ixs[ix_a], ixs[ix_b] = 1, 1
            pairs.append((ix_a, ix_b))

    # Get all the segs and map them by their IDs
    S = mode.getSegmentsById(ixs.keys())
    s_dict = {}
    for s in S: s_dict[s.ix] = s

    # Get the address and shared node ID of each cross street pair
    addrs = []
    node_ids = []
    for p in pairs:
        s, t = s_dict[p[0]], s_dict[p[1]]
        i_addr = deepcopy(addr)
        _setStreetAndPlaceFromSegment(i_addr.street1, i_addr.place1, s)
        _setStreetAndPlaceFromSegment(i_addr.street2, i_addr.place2, t)
        addrs.append(i_addr)
        node_ids.append(s.getIDOfSharedIntersection(t))

    # Get all the ints and map them by their Node IDs
    I = mode.getIntersectionsById(node_ids)
    i_dict = {}
    for i in I: i_dict[i.id] = i

    # Make a list of all the matching addresses and return it
    geocodes = []
    for addr, node_id in zip(addrs, node_ids):
        code = IntersectionGeocode(addr, i_dict[node_id])
        geocodes.append(code)
    return geocodes


## Helper functions

def _setStreetAndPlaceFromSegment(street, place, seg):
    attrs = seg.getAttrsOnSide('left')
    for attr in ('prefix', 'name', 'type', 'suffix'):
        street.__dict__[attr] = attrs[attr]
    for attr in ('city', 'id_state', 'zip'):
        place.__dict__[attr] = attrs[attr]


def _getPlaceWhere(place):
    where = []
    if place.ix_city:
        cid = place.ix_city
        where.append('(ix_city_l=%s OR ix_city_r=%s)' % (cid, cid))
    if place.id_state:
        sc = place.id_state
        where.append('(id_state_l="%s" OR id_state_r="%s")' % (sc, sc))
    if place.zip:
        z = place.zip
        where.append('(zip_l=%s OR zip_r=%s)' % (z, z))    
    return where
