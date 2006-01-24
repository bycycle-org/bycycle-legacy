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
                  'e': self.segment.id}
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
    streetname_ids = ','.join([str(i) for i in street.getIds(mode)])
    where.append('streetname_id IN (%s)' % streetname_ids)
    where = ' AND '.join(where)

    # Get segments matching inaddr
    Q = 'SELECT id FROM %s WHERE %s' % (mode.tables['edges'], where)
    mode.execute(Q)
    rows = mode.fetchAll()
    if rows: ids = [r[0] for r in rows]
    else: return []
    segs = mode.getSegmentsById(ids)

    # Make list of geocodes for segments matching inaddr
    geocodes = []
    for s in segs:
        s_addr = deepcopy(addr)
        attrs = s.getAttrsOnNumSide(addr.number)
        for attr in ('prefix', 'name', 'type', 'suffix'):
            s_addr.street.__dict__[attr] = attrs[attr]
        for attr in ('city', 'state_id', 'zip'):
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
    streetname_ids_a = ','.join([str(i) for i in street1.getIds(mode)])
    streetname_ids_b = ','.join([str(i) for i in street2.getIds(mode)])
    # Create the WHERE clause
    Q = 'SELECT id, node_f_id, node_t_id FROM %s WHERE' % mode.tables['edges']
    first = True
    for place, ids in ((place1, streetname_ids_a),
                       (place2, streetname_ids_b)):
        where = _getPlaceWhere(place)
        where.append('streetname_id IN (%s)' % ids)
        where = ' AND '.join(where)
        mode.executeDict('%s %s' % (Q, where))
        rows = mode.fetchAllDict()
        if not rows: return []
        if first:
            first = False
            rows_a = rows
        else:
            rows_b = rows

    # Index all segments by their fr/node_t_ids
    ia, ib = {}, {}
    for i, R in ((ia, rows_a), (ib, rows_b)):
        for r in R:
            id = r['id']
            node_f_id, node_t_id = r['node_f_id'], r['node_t_id']
            if node_f_id in i: i[node_f_id].append(id)
            else: i[node_f_id] = [id]
            if node_t_id in i: i[node_t_id].append(id)
            else: i[node_t_id] = [id]

    # Get IDs of segs with matching id
    ids, pairs = {}, []
    for id in ia:
        if id in ib:
            id_a, id_b = ia[id][0], ib[id][0]
            ids[id_a], ids[id_b] = 1, 1
            pairs.append((id_a, id_b))

    # Get all the segs and map them by their IDs
    S = mode.getSegmentsById(ids.keys())
    s_dict = {}
    for s in S: s_dict[s.id] = s

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

    
def getPointGeocodes(inaddr, mode):
    try:
        # Special case of node ID supplied directly
        min_id = int(inaddr)
        addr = address.PointAddress('(0,0)', mode)
    except ValueError:
        addr = address.PointAddress(inaddr, mode)
        x, y = addr.x, addr.y
        min_dist = 2000000000
        Q = 'SELECT id, wkt_geometry FROM %s' % (mode.tables['vertices'])
        mode.execute(Q)
        rows = mode.fetchAll()
        if rows:
            from math import sin, cos, acos, radians
            wkt_geoms = [row[1] for row in rows]
            points = gis.importWktGeometries(wkt_geoms, 'point')
            earth_radius = gis.earth_radius
            for i, row in enumerate(rows):
                id = row[0]
                point = points[i]
                dist = earth_radius * \
                       acos(cos(radians(y)) * \
                            cos(radians(point.y)) * \
                            cos(radians(point.x-x)) + \
                            sin(radians(y)) * \
                            sin(radians(point.y)))                
                if dist < min_dist:
                    min_id = id
                    min_dist = dist
                    if min_dist < .025: break  # close enough
        else:
            return []

    # Get segment rows that have our min_id as their node_f_id/t
    Q = 'SELECT id, streetname_id ' \
        'FROM %s WHERE node_f_id=%s OR node_t_id=%s' % \
        (mode.tables['edges'], min_id, min_id)
    mode.executeDict(Q)
    rows = mode.fetchAllDict()

    # Index segment rows by their street name IDs
    st_ids = {}
    for row in rows:
        streetname_id = row['streetname_id']
        if streetname_id in st_ids:
            st_ids[streetname_id].append(row['id'])
        else:
            st_ids[streetname_id] = [row['id']]

    i = mode.getIntersectionById(min_id)

    ids_a = st_ids.popitem()[1]
    if st_ids:
        ## Found point at intersection
        ids_b = st_ids.popitem()[1]
        # Get segments
        s, t = mode.getSegmentsById((ids_a[0], ids_b[0]))
        # Set address attributes
        _setStreetAndPlaceFromSegment(addr.street1, addr.place1, s)
        _setStreetAndPlaceFromSegment(addr.street2, addr.place2, t)
        # Get intersection
        code = IntersectionGeocode(addr, i)
    else:
        ## Found point at dead end
        addr = address.AddressAddress('', mode)
        s = mode.getSegmentById(ids_a[0])
        # Set address number to num at min_nid end of segment
        if min_id == s.node_f_id:
            addr.number = s.addr_f
            lon_lat = s.linestring[0]
        else:
            addr.number = s.addr_t
            lon_lat = s.linestring[-1]
        _setStreetAndPlaceFromSegment(addr.street, addr.place, s)
        code = AddressGeocode(addr, s, lon_lat)
        code.intersection = i
    return [code]


## Helper functions

def _setStreetAndPlaceFromSegment(street, place, seg):
    attrs = seg.getAttrsOnSide('left')
    for attr in ('prefix', 'name', 'type', 'suffix'):
        street.__dict__[attr] = attrs[attr]
    for attr in ('city', 'state_id', 'zip'):
        place.__dict__[attr] = attrs[attr]


def _getPlaceWhere(place):
    where = []
    if place.city_id:
        cid = place.city_id
        where.append('(city_l_id=%s OR city_r_id=%s)' % (cid, cid))
    if place.state_id:
        sc = place.id_state
        where.append('(state_l_id="%s" OR state_r_id="%s")' % (sc, sc))
    if place.zip:
        z = place.zip
        where.append('(zip_l=%s OR zip_r=%s)' % (z, z))    
    return where
