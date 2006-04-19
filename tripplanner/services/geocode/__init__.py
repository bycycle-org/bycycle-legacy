# Geocode Service Module

from byCycle.lib import gis
from byCycle.tripplanner.model import mode, address, geocode
from byCycle.tripplanner.services import excs, normaddr

class GeocodeError(excs.ByCycleError):
    def __init__(self, desc=''): 
        if not desc:
            desc = 'Geocode Error'
        excs.ByCycleError.__init__(self, desc)

class AddressNotFoundError(GeocodeError):
    def __init__(self, address=''):
        desc = 'Unable to find address "%s"' % address
        GeocodeError.__init__(self, desc=desc)
                
class MultipleMatchingAddressesError(GeocodeError):
    def __init__(self, geocodes=[]):
        self.geocodes = geocodes
        desc = 'Multiple matches found'
        GeocodeError.__init__(self, desc=desc)

 
def get(region='', q='', **params):
    """Get the geocode of the address, according to the data mode.
    
    Choose the geocoding function based on the type of the input address. Call
    the appropriate geocoding function. Return a list of Geocode objects or
    raise exception when no geocodes.

    @param string|object region Either the name of a region mode OR a mode
           object. In the first case a mode will be instantiated to geocode the
           address; in the second the object will be used directly.
    @param q An address string that can be normalized & geocoded in the mode
    @return A list of possible geocodes for the input address
    
    """
    # Check input
    errors = []

    if not region:
        errors.append('Please select a region')
            
    q = q.strip().lower()
    if not q:
        errors.append('Please enter an address')

    if errors:
        raise excs.InputError(errors)

    if not isinstance(region, mode.Mode):
        path = 'byCycle.tripplanner.model.%s'
        oMode = __import__(path % region, globals(), locals(), ['']).Mode()
    else:
        oMode = region

    try:
        oAddr = normaddr.get(region=oMode, q=q)
    except ValueError:
        pass
    else:
        if isinstance(oAddr, address.PostalAddress):
            geocodes = getPostalAddressGeocodes(oMode, oAddr)
        elif isinstance(oAddr, address.EdgeAddress):
            geocodes = getPostalAddressGeocodes(oMode, oAddr)
        elif isinstance(oAddr, address.IntersectionAddress):
            geocodes = getIntersectionGeocodes(oMode, oAddr)
        elif isinstance(oAddr, address.NodeAddress):
            geocodes = getPointGeocodes(oMode, oAddr)
        elif isinstance(oAddr, address.PointAddress):
            geocodes = getPointGeocodes(oMode, oAddr)
        
        if len(geocodes) > 1:
            raise MultipleMatchingAddressesError(geocodes)

        return geocodes

    raise ValueError('Could not find address "%s" in region "%s"'%(q, region))


# Each get*Geocode function returns a list of possible geocodes for the input
# address or raises an error when no matches are found.

def getPostalAddressGeocodes(oMode, oAddr, edge_id=None):
    place = oAddr.place

    # Build the WHERE clause
    where = []
    where.append('(%s BETWEEN LEAST(addr_f, addr_t) AND '
                 'GREATEST(addr_f, addr_t))' % oAddr.number)

    try:
        edge_id = oAddr.edge_id
    except AttributeError:
        where += _getPlaceWhere(place)
        streetname_ids = ','.join([str(i) for i in
                                   oMode.getStreetNameIds(oAddr.street)])
        where.append('streetname_id IN (%s)' % streetname_ids)
    else:
        where.append('id = %s' % edge_id)
        
    where = ' AND '.join(where)

    # Get segments matching oAddr
    Q = 'SELECT id FROM %s WHERE %s' % (oMode.tables['edges'], where)
    oMode.execute(Q)
    rows = oMode.fetchAll()
    if rows:
        ids = [r[0] for r in rows]
    else:
        raise AddressNotFoundError(oAddr)
    
    # Make list of geocodes for segments matching oAddr
    geocodes = []
    num = oAddr.number
    segs = oMode.getSegmentsById(ids)
    for s in segs:
        s_addr = address.PostalAddress(num)
        attrs = s.getAttrsOnNumSide(num)
        for attr in ('prefix', 'name', 'type', 'suffix'):
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

    
def getIntersectionGeocodes(oMode, oAddr):        
    street1, street2 = oAddr.street1, oAddr.street2
    place1, place2 = oAddr.place1, oAddr.place2
    streetname_ids_a = ','.join([str(i) for i in
                                 oMode.getStreetNameIds(street1)])
    streetname_ids_b = ','.join([str(i) for i in
                                 oMode.getStreetNameIds(street2)])
    # Create the WHERE clause
    Q = 'SELECT id, node_f_id, node_t_id FROM %s WHERE' % oMode.tables['edges']
    first = True
    for place, ids in ((place1, streetname_ids_a),
                       (place2, streetname_ids_b)):
        where = _getPlaceWhere(place)
        where.append('streetname_id IN (%s)' % ids)
        where = ' AND '.join(where)
        oMode.executeDict('%s %s' % (Q, where))
        rows = oMode.fetchAllDict()
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
    S = oMode.getSegmentsById(ids.keys())
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
    I = oMode.getIntersectionsById(node_ids)
    i_dict = {}
    for i in I: i_dict[i.id] = i

    # Make a list of all the matching addresses and return it
    geocodes = []
    for addr, node_id in zip(addrs, node_ids):
        code = geocode.IntersectionGeocode(addr, i_dict[node_id])
        geocodes.append(code)
    return geocodes

    
def getPointGeocodes(oMode, oAddr):
    try:
        # Special case of node ID supplied directly
        min_id = oAddr.node_id
    except AttributeError:
        Q = 'SELECT id, ' \
            'GLength(LineStringFromWKB(LineString(' \
            'AsBinary(geom), AsBinary(geomfromtext("%s"))))) ' \
            'AS distance ' \
            'FROM %s ORDER BY distance ASC LIMIT 1'
        oMode.execute(Q % (oAddr.point, oMode.tables['nodes']))
        row = oMode.fetchRow()
        min_id = row[0]

    # Get segment rows that have our min_id as their node_f_id/t
    Q = 'SELECT id, streetname_id ' \
        'FROM %s WHERE node_f_id=%s OR node_t_id=%s' % \
        (oMode.tables['edges'], min_id, min_id)
    oMode.executeDict(Q)
    rows = oMode.fetchAllDict()

    # Index segment rows by their street name IDs
    st_ids = {}
    for row in rows:
        streetname_id = row['streetname_id']
        if streetname_id in st_ids:
            st_ids[streetname_id].append(row['id'])
        else:
            st_ids[streetname_id] = [row['id']]

    i = oMode.getIntersectionById(min_id)

    ids_a = st_ids.popitem()[1]
    if st_ids:
        # Found point at intersection
        ids_b = st_ids.popitem()[1]
        # Get segments
        s, t = oMode.getSegmentsById((ids_a[0], ids_b[0]))
        # Set address attributes
        _setStreetAndPlaceFromSegment(oAddr.street1, oAddr.place1, s)
        _setStreetAndPlaceFromSegment(oAddr.street2, oAddr.place2, t)
        # Get intersection
        code = geocode.IntersectionGeocode(addr, i)
    else:
        # Found point at dead end
        addr = address.PostalAddress('', mode)
        s = oMode.getSegmentById(ids_a[0])
        # Set address number to num at min_nid end of segment
        if min_id == s.node_f_id:
            addr.number = s.addr_f
            lon_lat = s.linestring[0]
        else:
            addr.number = s.addr_t
            lon_lat = s.linestring[-1]
        _setStreetAndPlaceFromSegment(addr.street, addr.place, s)
        code = geocode.PostalGeocode(addr, s, lon_lat)
        code.intersection = i
    return [code]


## Helper functions

def _setStreetAndPlaceFromSegment(street, place, seg):
    attrs = seg.getAttrsOnSide('left')
    for attr in ('prefix', 'name', 'type', 'suffix'):
        street.__dict__[attr] = attrs[attr]
    for attr in ('city_id', 'city', 'state_id', 'zip_code'):
        place.__dict__[attr] = attrs[attr]


def _getPlaceWhere(place):
    where = []
    if place.city_id is not None:
        cid = place.city_id
        where.append('(city_l_id=%s OR city_r_id=%s)' % (cid, cid))
    if place.state_id:
        st = place.state_id
        print st
        where.append('(state_l_id="%s" OR state_r_id="%s")' % (st, st))
    if place.zip_code:
        z = place.zip_code
        where.append('(zip_code_l=%s OR zip_code_r=%s)' % (z, z))
    return where





# TODO: Move to separate test module
if __name__ == "__main__":
    # TODO: Create unit tests!!!!
    
    import sys
    import time

    try:
        region, q = sys.argv[1].split(',')
    except IndexError:
        A = {#' ',
            # Milwaukee
            'milwaukeewi':
            ('0 w hayes ave',
             'lon=-87.940407, lat=43.05321',
             'lon=-87.931137, lat=43.101234',
             'lon=-87.934399, lat=43.047126',
             '125 n milwaukee',
             '125 n milwaukee milwaukee wi',
             '27th and lisbon',
             '27th and lisbon milwaukee',
             '27th and lisbon milwaukee, wi',
             'lon=-87.961178, lat=43.062993',
             'lon=-87.921953, lat=43.040791',
             'n 8th st & w juneau ave, milwaukee, wi ',
             '77th and burleigh',
             '2750 lisbon',
             '(-87.976885, 43.059544)',
             'lon=-87.946243, lat=43.041669',
             '124th and county line',
             '124th and county line wi',
             '5th and center',
             '6th and hadley',
             ),
            
            'portlandor':
            ('633 n alberta',
             'point(-120.432129 46.137977)',
             'point(-120.025635 45.379161)',
             '300 main',
             '4550 ne 15',
             '4550 ne 15th',
             '37800 S Hwy 213 Hwy, Clackamas, OR 97362',
             '4408 se stark',
             '4408 se stark, or',
             '4408 se stark, wi',
             '4408 se stark st oregon 97215',
             '44th and stark',
             '3 and main oregon',
             '3rd & main 97024',
             '(-122.67334, 45.523307)',
             'W Burnside St, Portland, OR 97204 & ' \
             'NW 3rd Ave, Portland, OR 97209',
             'Burnside St, Portland, & 3rd Ave, Portland, OR 97209',
             '300 bloofy lane',
             ),
            }
    else:
        A = {region: (q,)}

    i = 1
    for region in ('portlandor',):
        print
        print 'Data region: %s' % region
        print '------------------------------'
        for q in A[region]:
            st = time.time()
            try:
                geocodes = get(region=region, q=q)
            except AddressNotFoundError, e:
                print i, q
                print e
            except MultipleMatchingAddressesError, e:
                print i, q
                print e
                for code in e.geocodes:
                    print '%s' % code
            except Exception, e:
                print e
            else:
                print i, q
                try:
                    print '%s' % geocodes[0]
                except IndexError:
                    print 'No geocodes'
            i+=1
            tt = time.time() - st
            print '%.2f seconds' % tt 
            print
