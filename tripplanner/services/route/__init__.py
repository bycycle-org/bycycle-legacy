# Route Service Module
# 28 Dec 2004
import time
from byCycle.lib import gis
from byCycle.tripplanner.model import address, intersection
from byCycle.tripplanner.services import excs, geocode
import sssp

travel_modes = {'bike': 'bicycle',
                'bicycle': 'bicycle',
                'walk': 'pedestrian',
                'pedestrian': 'pedestrian',
                'drive': 'automobile',
                'car': 'automobile',
                'auto': 'automobile'}
data_modes = {'metro': 'metro',
              'milwaukee': 'milwaukee'}


class RouteError(Exception):
    def __init__(self, desc=''):
        if desc: self.description = desc
        else: self.description = 'Route Error'

    def __str__(self):
        return self.description

class NoRouteError(RouteError):
    def __init__(self, desc=''):
        RouteError.__init__(self, desc=desc)
            
class MultipleMatchingAddressesError(RouteError):
    def __init__(self, geocodes={'from': [], 'to': []}):
        self.geocodes = geocodes
        desc = 'Multiple matches found'
        RouteError.__init__(self, desc=desc)


def get(input={}):
    st_tot = time.time()
    messages, errors = [], []
            
    ## Get necessary data from input
    # q -- list of route points (currently only 2 supported)
    # dmode -- data mode (TODO: should be determined from place in geocoder)
    # tmode -- travel mode
    # options -- dict of optional user options (sent off to tmode)
    try: q = input['q']
    except KeyError: errors.append('Route query required')
    else:
        try: fr = q[0]
        except IndexError: errors.append('Start address required')
        try: to = q[1]
        except IndexError: errors.append('End address required')
        
    try: dmode = input['dmode']
    except KeyError: errors.append('Data mode required')
    else:
        try: dmode = data_modes[dmode]
        except KeyError: errors.append('Unknown data mode')

    try: tmode = input['tmode']
    except KeyError: errors.append('Travel mode required')
    else:
        try: tmode = travel_modes[tmode]
        except KeyError: errors.append('Unknown travel mode')

    # Let multiple input errors fall through to here
    if errors: raise excs.InputError(errors)

    # The mode is a combination of the data/travel modes
    path = 'byCycle.tripplanner.model.%s.%s'
    mode = __import__(path % (dmode, tmode), globals(), locals(), ['']).Mode()


    ## Get geocodes matching from and to addresses
    M = {'from': [], 'to': []}
    try:
        fcodes = geocode.get({'q': fr, 'dmode': mode})
    except geocode.AddressNotFoundError, e:
        errors.append(e.description)
    except geocode.MultipleMatchingAddressesError, e:
        M['from'] = e.geocodes
    try:
        tcodes = geocode.get({'q': to, 'dmode': mode})
    except geocode.AddressNotFoundError, e:
        errors.append(e.description)
    except geocode.MultipleMatchingAddressesError, e:
        M['to'] = e.geocodes
    if M['from'] or M['to']: raise MultipleMatchingAddressesError(M)

    # Let multiple multiple match errors fall through to here
    if errors: raise excs.InputError(errors)

    # Precise (enough) addresses were entered
    fcode, tcode = fcodes[0], tcodes[0]

    # TODO: Make this check actually work
    if fcode == tcode:
        raise excs.InputError('Start and End appear to be the same')


    ## Made it through that maze--now fetch the main adjacency matrix, G
    st = time.time()
    G = mode.getAdjacencyMatrix()
    if not G: raise NoRouteError('Graph is empty')
    messages.append('Time to get G: %s' % (time.time() - st))


    ## Create the auxillary adjacency matrix, H
    def __getIntersectionForGeocode(geocode, nid, eid1, eid2):
        """
        
        Args
        nid -- shared node ID at split
        eid1 -- segment id for node-->nid segment
        eid2 -- segment id for nid-->other_node segment

        Return
        An intersection object at at the split with a node ID of nid
        
        """
        try:
            # Geocode is at an intersection--easy case
            i = geocode.intersection
        except AttributeError:
            # Geocode is in a segment--hard case
            # We have to generate an intersection in the middle of the segment
            # and add data to G (by adding that data to H so G can remain
            # unmodified)
            #
            # Split the geocode's segment
            seg = geocode.segment
            num = geocode.address.number
            fn_seg, nt_seg = seg.splitAtNum(num)
            fn_seg.rowid, nt_seg.rowid = eid1, eid2
            split_segs[eid1], split_segs[eid2] = fn_seg, nt_seg
            fnode, tnode = seg.fnode, seg.tnode
            #
            # Create an intersection at the split
            st = seg.street
            st.number = num
            data = {'nid': nid,
                    'cross_streets': [st],
                    'lon_lat': nt_seg.linestring[0]}
            i = intersection.Intersection(data)
            #
            # Update H's nodes
            __updateHNodes(fnode, nid, tnode, eid1, eid2)
            __updateHNodes(tnode, nid, fnode, eid2, eid1)
            #
            # Update H's edges
            eid = seg.rowid
            H_edges[eid1] = [fn_seg.getWeight()] + list(G_edges[eid][1:])
            H_edges[eid2] = [nt_seg.getWeight()] + list(G_edges[eid][1:])
        return i

    def __updateHNodes(nid1, nid, nid2, eid1, eid2):
        try:
            G_nodes[nid1][nid2]
        except KeyError:
            # nid1 does NOT go to nid2--nothing to do
            pass
        else:
            # nid1 DOES go to nid2
            H_nodes[nid1], H_nodes[nid] = G_nodes[nid1], {}
            H_nodes[nid1][nid] = eid1
            H_nodes[nid][nid2] = eid2
            # override original connection so it won't be used
            H_nodes[nid1][nid2] = None  

    split_segs = {}
    H = {'nodes': {}, 'edges': {}}
    G_nodes, G_edges = G['nodes'], G['edges']
    H_nodes, H_edges = H['nodes'], H['edges']
    fint = __getIntersectionForGeocode(fcode, -1, -1, -2)
    tint = __getIntersectionForGeocode(tcode, -2, -3, -4)
    fnode, tnode = fint.nid, tint.nid

    
    ## Try to find a path
    st = time.time()
    try:
        V, E, W, w = sssp.findPath(G, H, fnode, tnode,
                                   weightFunction=mode.getEdgeWeight,
                                   heuristicFunction=None)
    except sssp.SingleSourceShortestPathsNoPathError:
        raise NoRouteError('Could not find a route')
    messages.append('Time to getPath: %s' % (time.time() - st))


    ## A path was found
    ## Get intersections and segments along path
    st = time.time()
    I = mode.getIntersectionsById(V)
    if I[0] is None: I[0] = fint
    if I[-1] is None: I[-1] = tint
    S = mode.getSegmentsById(E)
    if S[0] is None: S[0] = split_segs[E[0]]
    if S[-1] is None: S[-1] = split_segs[E[-1]]
    
    messages.append('Time to fetch ints and segs by ID %s' % (time.time()-st))


    ## Convert route data to output format
    directions = makeDirections(I, S)
    messages.append('Time to make directions: %s' % (time.time() - st))
    route = {'from':       {'geocode': fcode, 'original': fr},
             'to':         {'geocode': tcode, 'original': to},
             'linestring': [],
             'directions': [],
             'distance':   {},
             'messages': []
             }
    route.update(directions)
    messages.append('Total time: %s' % (time.time() - st_tot))
    route['messages'] = messages
    return route


# -----------------------------------------------------------------------------

def makeDirections(I, S):
    """Process the shortest path into a nice list of directions.

    @param S -- the segments on the route
    @param I -- the intersections on the route
    @return -- A dict containing...
                 - a list of directions. Each direction has the following form:
                   {
                      'turn': 'left',
                      'street': 'se stark st'
                      'toward': 'se 45th ave'
                      'ls_index': 3,
                      'distance': {'mi': .03,
                                   'km': .05,
                                   'blocks': 0},
                      'bikemode': 'bl',
                      'jogs': [{'turn': 'left', 'street': 'ne 7th ave'}, ...]
                    }
                  - a linestring, which is a list of x, y coords. Each coord
                    has the following form:
                    {
                       'x': -122,
                       'y': -45
                    }
                  - a dict of total distances in units of miles, kilometers,
                    and blocks, e.g.:
                    {
                       'mi': .45,
                       'km': .73,
                       'blocks': 9
                    }
                    
    """
    directions = []
    linestring = []
    distance = {}

    # Get the actual segment weights since modified weights might have been
    # used to find the route
    W = [s.getWeight() for s in S]
    w = reduce(lambda x, y: x + y, W)
    mi = '%.2f' % w
    km = '%.2f' % (w * 1.609344)
    blocks = int(round(w / .05))

    # Get bearing of travel for each segment
    bearings = []
    end_bearings = []
    last_fri = I[-2]
    for (toi, s) in zip(I[1:], S):
        # Get the bearing of the segment--based on whether we are moving
        # toward its start or end
        # Assume moving fr => to
        frlonlat, tolonlat = s.linestring[0], s.linestring[1]
        e_frlonlat, e_tolonlat = s.linestring[-2], s.linestring[-1]
        sls = s.linestring

        if (toi and s.fnode == toi.nid) or \
               (not toi and last_fri and s.tnode == last_fri.nid):
            # Assumption wrong: moving to => fr
            frlonlat, tolonlat = tolonlat, frlonlat
            e_frlonlat, e_tolonlat = e_tolonlat, e_frlonlat
            sls.reverse()

        # This avoids duplicate x,y at intersections--below we'll have to
        # append the last point for the last segment
        linestring += [{'x': p.x, 'y': p.y} for p in sls[:-1]]
        bearing = gis.getBearingGivenStartAndEndPoints(frlonlat, tolonlat)
        bearings.append(bearing)
        end_bearing = gis.getBearingGivenStartAndEndPoints(e_frlonlat,
                                                           e_tolonlat)
        end_bearings.append(end_bearing)
    # Append the very last point in the route
    p = sls[-1]
    linestring.append({'x': p.x, 'y': p.y})
    
    # Add the lengths of successive same-named segments and set the first of
    # the segments' length to that 'stretch' length, while setting the
    # successive segments' lengths to 0. In the next for loop below,
    # segments with length 0 are skipped.
    prev_name_type = ''
    seg_x = stretch_start_x = 0
    streets = []
    jogs = []
    for s in S:
        st = address.Street(s.prefix, s.name, s.type, s.suffix)
        streets.append(st)  # save for later
        name_type = '%s %s' % (s.name, s.type)

        try: next_s = S[seg_x + 1]
        except IndexError: next_name_type = '!@#$'
        else: next_name_type = '%s %s' % (next_s.name, next_s.type)
        
        if name_type == prev_name_type:
            W[stretch_start_x] += W[seg_x]
            W[seg_x] = 0
            prev_name_type = name_type
        # Check for jog
        elif prev_name_type and \
                 W[seg_x] < .05 and name_type != prev_name_type and \
                 next_name_type == prev_name_type:
            W[stretch_start_x] += W[seg_x]
            W[seg_x] = 0
            turn = calculateWayToTurn(bearings[seg_x], end_bearings[seg_x - 1])
            jogs[-1].append({'turn': turn, 'street': str(st)})
        else:
            # Start of a new stretch (i.e., a new direction)
            stretch_start_x = seg_x
            prev_name_type = name_type
            jogs.append([])
            
        seg_x += 1


    # Add 'stretches' between start and destination intersections
    # (where a stretch consists of one or more segments that all have
    #  the same name and type)
    s_count = 0
    d_count = 0
    extra = []
    for (toi, s, w) in zip(I[1:], S, W):        
        st = streets[s_count]
        st_str = str(st)
        
        if w:
            # Things in here only happen at the start of a stretch

            bearing = bearings[s_count]

            d = {'turn': '',
                 'street': '',
                 'toward': '',
                 'ls_index': s_count,
                 'distance': {'mi': '%.2f' % w,
                              'km': '%.2f' % (1.609344 * w),
                              'blocks': 0},
                 'bikemode': '',
                 'jogs': jogs[d_count]
                 }

            # Get direction of turn and street to turn onto
            if directions:
                # Common case (i.e., all but first)
                turn = calculateWayToTurn(bearing, stretch_end_bearing)
                if turn == 'straight':
                    # go straight onto next st. ('street a becomes street b')
                    street = [stretch_end_name, st_str]
                else:
                    # turn onto next street
                    street = st_str
            else:
                # The first direction is a bit different from the rest
                turn = getDirectionFromBearing(bearing)
                street = st_str

            # Get a street name for the intersection we're headed toward
            # (one different from the name of the current seg)
            if toi: toward = getDifferentNameInIntersection(st, toi)
            else: toward = ''

            for item in ('turn', 'street', 'toward'): d[item] = eval(item)
            
            directions.append(d)
            d_count += 1

        # Save bearing if this segment is the last segment in a stretch
        try:
            if toi and W[s_count+1]:
                stretch_end_bearing = end_bearings[s_count] 
                stretch_end_name = st_str
        except IndexError:
            pass

        s_count += 1

    return {'directions': directions,
            'linestring': linestring,
            'distance': {'mi': mi, 'km': km, 'blocks': blocks}}


def getDifferentNameInIntersection(st, i):
    """Get street name from intersection that is different from street st."""
    for i_st in i.cross_streets:
        if st.name != i_st.name and st.type != i_st.type:
            return str(st)
    return ''


def calculateWayToTurn(new_bearing, old_bearing):
    """Given two bearings in [0, 360], gives the turn to go from old to new.

    @param new_bearing -- the bearing of the new direction of travel
    @param old_bearing -- the bearing of the old direction of travel
    @return -- the way to turn to get from going in the old direction
               to get going in the new direction ('right', 'left', etc.)

    """
    diff = new_bearing - old_bearing
    while diff < 0: diff += 360
    while diff > 360: diff -= 360
    if     0 <= diff <   10: way = 'straight'
    elif  10 <= diff <= 170: way = 'right'
    elif 170 <  diff <  190: way = 'back'
    elif 190 <= diff <= 350: way = 'left'
    elif 350 <  diff <= 360: way = 'straight'
    else: way = 'ERROR'
    return way


def getDirectionFromBearing(bearing):
    arc = 45
    half_arc = arc * .5
    n =  (360 - half_arc, half_arc)
    ne = (n[1],  n[1]  + arc)
    e =  (ne[1], ne[1] + arc)
    se = (e[1],  e[1]  + arc)
    s =  (se[1], se[1] + arc)
    sw = (s[1],  s[1]  + arc)
    w =  (sw[1], sw[1] + arc)
    nw = (w[1],  w[1]  + arc)
    if   n[0]  < bearing <= 360 or 0 <= bearing < n[1]: return 'north'
    elif ne[0] < bearing <= ne[1]: return 'northeast'
    elif e[0]  < bearing <= e[1]:  return 'east'
    elif se[0] < bearing <= se[1]: return 'southeast'
    elif s[0]  < bearing <= s[1]:  return 'south'
    elif sw[0] < bearing <= sw[1]: return 'southwest'
    elif w[0]  < bearing <= w[1]:  return 'west'
    elif nw[0] < bearing <= nw[1]: return 'northwest'


def print_key(key):
    for k in key:
        print k, 
        if type(key[k]) == type({}):
            print
            for l in key[k]:
                print '\t', l, key[k][l]
        else: print key[k]
    print


if __name__ == '__main__':
    q = ['N 8th St & W Juneau Ave, Milwaukee, WI',
         'N 25th St & W Brown St, Milwaukee, WI 53205'
         ]
    dm = 'milwaukee'
    tm = 'bike'
    try:
        result = get({'q': q, 'dmode': dm, 'tmode': tm})
    except Exception, e:
        #print e
        raise
    else:
        fr = result['from']
        print_key(fr)
        print_key(result['to'])
