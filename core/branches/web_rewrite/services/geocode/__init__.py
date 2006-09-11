"""$Id$

Geocode Service Module.

Copyright (C) 2006 Wyatt Baldwin, byCycle.org <wyatt@bycycle.org>. All rights 
reserved. Please see the LICENSE file included in the distribution. The license 
is also available online at http://bycycle.org/tripplanner/license.txt or by 
writing to license@bycycle.org.

"""
from byCycle.lib import gis
from byCycle.model import mode, address, geocode
from byCycle.services import excs, normaddr


class GeocodeError(excs.ByCycleError):
    def __init__(self, desc=''): 
        if not desc:
            desc = 'Geocode Error'
        excs.ByCycleError.__init__(self, desc)

class AddressNotFoundError(GeocodeError):
    def __init__(self, region='', address=''):
        desc = 'Unable to find address "%s" in region "%s"' % (address, region)
        GeocodeError.__init__(self, desc=desc)
                
class MultipleMatchingAddressesError(GeocodeError):
    def __init__(self, geocodes=[]):
        self.geocodes = geocodes
        desc = 'Multiple matches found'
        GeocodeError.__init__(self, desc=desc)

 
def get(q, region=''):
    """Get the geocode of the address, according to the data mode.
    
    Choose the geocoding function based on the type of the input address. Call
    the appropriate geocoding function. Return a list of Geocode objects or
    raise exception when no geocodes.

    @param region Either the name of a region mode OR a mode
           object. In the first case a mode will be instantiated to geocode the
           address; in the second the object will be used directly.
    @param q An address string that can be normalized & geocoded in the mode
    @return A list of possible geocodes for the input address OR raise
            AddressNotFoundError if the address can't be geocoded
    
    """
    oAddr = normaddr.get(q=q, region=region)
    oRegion = oAddr.region

    if isinstance(oAddr, address.PostalAddress):
        geocodes = getPostalAddressGeocodes(oRegion, oAddr)
    elif isinstance(oAddr, address.EdgeAddress):
        geocodes = getPostalAddressGeocodes(oRegion, oAddr)
    elif isinstance(oAddr, address.PointAddress):
        geocodes = getPointGeocodes(oRegion, oAddr)
    elif isinstance(oAddr, address.NodeAddress):
        geocodes = getPointGeocodes(oRegion, oAddr)
    elif isinstance(oAddr, address.IntersectionAddress):
        try:
            geocodes = getIntersectionGeocodes(oRegion, oAddr)
        except AddressNotFoundError, e:
            try:
                num = int(oAddr.name1[:-2])
            except (TypeError, ValueError):
                try:
                    num = int(oAddr.name2[:-2])
                except (TypeError, ValueError):
                    pass
                else:
                    street=oAddr.street1
            else:
                street = oAddr.street2
            try:
                oAddr = address.PostalAddress(number=num*100,
                                              street=street,
                                              place=oAddr.place1)
                geocodes = getPostalAddressGeocodes(oRegion, oAddr)
            except (NameError, AddressNotFoundError):
                raise e
    else:
        raise ValueError('Could not determine address type for address "%s" '
                         'in region "%s"' % (q, region))
        
    if len(geocodes) > 1:
        raise MultipleMatchingAddressesError(geocodes)
    
    return geocodes


# Each get*Geocode function returns a list of possible geocodes for the input
# address or raises an error when no matches are found.

def getPostalAddressGeocodes(oRegion, oAddr, edge_id=None):
    place = oAddr.place

    # Build the WHERE clause
    where = []
    where.append('(%s BETWEEN LEAST(addr_f, addr_t) AND '
                 'GREATEST(addr_f, addr_t))' % oAddr.number)
    
    try:
        # Number EdgeID
        where.append('id = %s' % oAddr.edge_id)
    except AttributeError:
        # Number Street Place
        try:
            ids = oRegion.getStreetNameIds(oAddr.street)
        except ValueError:
            raise AddressNotFoundError(oRegion, oAddr)
        else:
            streetname_ids = ','.join([str(i) for i in ids])
            where.append('streetname_id IN (%s)' % streetname_ids)
        where += _getPlaceWhere(place)
        
    where = ' AND '.join(where)

    # Get segments matching oAddr
    Q = 'SELECT id FROM %s WHERE %s' % (oRegion.tables['edges'], where)
    oRegion.execute(Q)
    rows = oRegion.fetchAll()
    if rows:
        ids = [r[0] for r in rows]
    else:
        raise AddressNotFoundError(oRegion, oAddr)
    
    # Make list of geocodes for segments matching oAddr
    geocodes = []
    num = oAddr.number
    segs = oRegion.getSegmentsById(ids)
    for s in segs:
        s_addr = address.PostalAddress(num)
        attrs = s.getAttrsOnNumSide(num)
        for attr in ('prefix', 'name', 'sttype', 'suffix'):
            setattr(s_addr.street, attr, attrs[attr])
        for attr in ('city_id', 'city', 'state_id', 'zip_code'):
            setattr(s_addr.place, attr, attrs[attr])
        xy = gis.getInterpolatedXY(s.linestring,
                                   max(s.addr_f, s.addr_t) -
                                   min(s.addr_f, s.addr_t),
                                   num -
                                   min(s.addr_f, s.addr_t))
        code = geocode.PostalGeocode(s_addr, s, xy)
        geocodes.append(code)
    return geocodes

    
def getIntersectionGeocodes(oRegion, oAddr):        
    street1, street2 = oAddr.street1, oAddr.street2
    place1, place2 = oAddr.place1, oAddr.place2

    try:
        ids_a = oRegion.getStreetNameIds(street1)
        ids_b = oRegion.getStreetNameIds(street2)
    except ValueError:
        raise AddressNotFoundError(oRegion, oAddr)
    else:
        streetname_ids_a = ','.join([str(i) for i in ids_a])
        streetname_ids_b = ','.join([str(i) for i in ids_b])

    # Create the WHERE clause
    Q = 'SELECT id, node_f_id, node_t_id FROM %s WHERE' % \
        oRegion.tables['edges']
    first = True
    for place, ids in ((place1, streetname_ids_a),
                       (place2, streetname_ids_b)):
        where = _getPlaceWhere(place)
        where.append('streetname_id IN (%s)' % ids)
        where = ' AND '.join(where)
        oRegion.executeDict('%s %s' % (Q, where))
        rows = oRegion.fetchAllDict()
        if not rows:
            raise AddressNotFoundError(oRegion, oAddr)
        if first:
            first = False
            rows_a = rows
        else:
            rows_b = rows

    # Index all segments by their node_f/t_ids
    ia, ib = {}, {}
    for i, R in ((ia, rows_a), (ib, rows_b)):
        for r in R:
            id = r['id']
            node_f_id, node_t_id = r['node_f_id'], r['node_t_id']
            if node_f_id in i:
                i[node_f_id].append(id)
            else:
                i[node_f_id] = [id]
            if node_t_id in i:
                i[node_t_id].append(id)
            else:
                i[node_t_id] = [id]

    # Get IDs of segs with matching id
    ids, pairs = {}, []
    for id in ia:
        if id in ib:
            id_a, id_b = ia[id][0], ib[id][0]
            ids[id_a], ids[id_b] = 1, 1
            pairs.append((id_a, id_b))
    if not pairs:
        raise AddressNotFoundError(oRegion, oAddr)

    # Get all the segs and map them by their IDs
    S = oRegion.getSegmentsById(ids.keys())
    if not S:
        raise AddressNotFoundError(oRegion, oAddr) 
    s_dict = {}
    for s in S: s_dict[s.id] = s

    # Get the address and shared node ID of each cross street pair
    addrs = []
    node_ids = []
    for p in pairs:
        s, t = s_dict[p[0]], s_dict[p[1]]
        i_addr = address.IntersectionAddress()
        _setStreetAndPlaceFromSegment(i_addr.street1, i_addr.place1, s)
        _setStreetAndPlaceFromSegment(i_addr.street2, i_addr.place2, t)
        addrs.append(i_addr)
        node_ids.append(s.getIDOfSharedIntersection(t))

    # Get all the ints and map them by their Node IDs
    I = oRegion.getIntersectionsById(node_ids)
    if not I:
        raise AddressNotFoundError(oRegion, oAddr)
    i_dict = {}
    for i in I:
        i_dict[i.id] = i

    # Make a list of all the matching addresses and return it
    geocodes = []
    for addr, node_id in zip(addrs, node_ids):
        code = geocode.IntersectionGeocode(addr, i_dict[node_id])
        geocodes.append(code)
    return geocodes

    
def getPointGeocodes(oRegion, oAddr):
    try:
        # Special case of node ID supplied directly
        min_id = oAddr.node_id
    except AttributeError:
        Q = 'SELECT id, ' \
            'GLength(LineStringFromWKB(LineString(' \
            'AsBinary(geom), AsBinary(geomfromtext("%s"))))) ' \
            'AS distance ' \
            'FROM %s ORDER BY distance ASC LIMIT 1'
        oRegion.execute(Q % (oAddr.point, oRegion.tables['nodes']))
        row = oRegion.fetchRow()
        min_id = row[0]

    # Get segment rows that have our min_id as their node_f_id/t
    Q = 'SELECT id, streetname_id ' \
        'FROM %s WHERE node_f_id=%s OR node_t_id=%s' % \
        (oRegion.tables['edges'], min_id, min_id)
    oRegion.executeDict(Q)
    rows = oRegion.fetchAllDict()

    if not rows:
       raise AddressNotFoundError(oRegion, oAddr)         

    # Index segment rows by their street name IDs
    st_ids = {}
    for row in rows:
        streetname_id = row['streetname_id']
        if streetname_id in st_ids:
            st_ids[streetname_id].append(row['id'])
        else:
            st_ids[streetname_id] = [row['id']]

    i = oRegion.getIntersectionById(min_id)

    ids_a = st_ids.popitem()[1]
    if st_ids:
        # Found point at intersection
        ids_b = st_ids.popitem()[1]
        # Get segments
        s, t = oRegion.getSegmentsById((ids_a[0], ids_b[0]))
        # Set address attributes
        _setStreetAndPlaceFromSegment(oAddr.street1, oAddr.place1, s)
        _setStreetAndPlaceFromSegment(oAddr.street2, oAddr.place2, t)
        # Make geocode
        code = geocode.IntersectionGeocode(oAddr, i)
    else:
        # Found point at dead end
        oAddr = address.PostalAddress()
        s = oRegion.getSegmentById(ids_a[0])
        # Set address number to num at min_nid end of segment
        if min_id == s.node_f_id:
            oAddr.number = s.addr_f
            xy = s.linestring[0]
        else:
            oAddr.number = s.addr_t
            xy = s.linestring[-1]
        _setStreetAndPlaceFromSegment(oAddr.street, oAddr.place, s)
        code = geocode.PostalGeocode(oAddr, s, xy)
        code.intersection = i
    return [code]


## Helper functions

def _setStreetAndPlaceFromSegment(street, place, seg):
    attrs = seg.getAttrsOnSide('left')
    for attr in ('prefix', 'name', 'sttype', 'suffix'):
        street.__dict__[attr] = attrs[attr]
    for attr in ('city_id', 'city', 'state_id', 'zip_code'):
        place.__dict__[attr] = attrs[attr]


def _getPlaceWhere(place):
    where = []
    if place.city and place.city_id:
        cid = place.city_id
        where.append('(city_l_id=%s OR city_r_id=%s)' % (cid, cid))
    if place.state_id:
        st = place.state_id
        where.append('(state_l_id="%s" OR state_r_id="%s")' % (st, st))
    if place.zip_code:
        z = place.zip_code
        where.append('(zip_code_l=%s OR zip_code_r=%s)' % (z, z))
    return where
