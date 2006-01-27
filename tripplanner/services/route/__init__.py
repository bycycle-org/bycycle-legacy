# Route Service Module
# 28 Dec 2004

import time
from byCycle.lib import gis
from byCycle.tripplanner.model import address, intersection
from byCycle.tripplanner.services import geocode
import sssp


travel_modes = {'bike': 'bicycle',
                'bicycle': 'bicycle',
                'walk': 'pedestrian',
                'pedestrian': 'pedestrian',
                'drive': 'automobile',
                'car': 'automobile',
                'auto': 'automobile'}

data_modes = {'portlandor': 'portlandor',
              'portland': 'portlandor',
              'metro': 'portlandor',
              'milwaukeewi': 'milwaukeewi',
              'milwaukee': 'milwaukeewi',
              }


class RouteError(Exception):
    def __init__(self, desc=''):
        if desc: self.description = desc
        else: self.description = 'Route Error'
    def __str__(self):
        return self.description

class NoRouteError(RouteError):
    def __init__(self, desc=''):
        RouteError.__init__(self, desc=desc)

class InputError(RouteError):
    def __init__(self, errors=[]):
        desc = '<br/>'.join(errors)
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
    # region -- data mode (TODO: should be determined from place in geocoder) 
    # tmode -- travel mode
    # options -- dict of optional user options (sent off to tmode)
    try: q = input['q']
    except KeyError: errors.append('Route query required')
    else:
        try:
            fr = q[0].strip()
            if not fr: raise IndexError
        except IndexError:
            errors.append('Start address required')
        try:
            to = q[1].strip()
            if not to: raise IndexError
        except IndexError:
            errors.append('End address required')

    try:
        region = input['region']
    except KeyError:
        errors.append('Data mode required')
    else:
        try: region = data_modes[region]
        except KeyError: errors.append('Unknown data mode')        
    try:
        tmode = input['tmode']
    except KeyError:
        errors.append('Travel mode required')
    else:
        try: tmode = travel_modes[tmode]
        except KeyError: errors.append('Unknown travel mode')

    # Let multiple input errors fall through to here
    if errors: raise InputError(errors)

    # The mode is a combination of the data/travel modes
    st = time.time()
    path = 'byCycle.tripplanner.model.%s.%s'
    mode = __import__(path % (region, tmode), globals(), locals(), ['']).Mode()
    messages.append('Time to instantiate mode: %s' % (time.time() - st))


    ## Get geocodes matching from and to addresses
    M = {'from': [], 'to': []}
    
    st = time.time()
    try:
        fcodes = geocode.get({'q': fr, 'region': mode})
    except geocode.AddressNotFoundError, e:
        errors.append(e.description)
    except geocode.MultipleMatchingAddressesError, e:
        M['from'] = e.geocodes
    messages.append('Time to get from address: %s' % (time.time() - st))        

    st = time.time()
    try:
        tcodes = geocode.get({'q': to, 'region': mode})
    except geocode.AddressNotFoundError, e:
        errors.append(e.description)
    except geocode.MultipleMatchingAddressesError, e:
        M['to'] = e.geocodes
    if M['from'] or M['to']: raise MultipleMatchingAddressesError(M)
    messages.append('Time to get to address: %s' % (time.time() - st))

    # Let multiple multiple match errors fall through to here
    if errors: raise InputError(errors)

    # Precise (enough) addresses were entered
    fcode, tcode = fcodes[0], tcodes[0]

    # TODO: Make this check actually work
    if fcode == tcode:
        raise InputError('Start and End appear to be the same')


    ## Made it through that maze--now fetch the main adjacency matrix, G
    st = time.time()
    G = mode.getAdjacencyMatrix()
    if not G: raise NoRouteError('Graph is empty')
    messages.append('Time to get G: %s' % (time.time() - st))


    ## Get or synthesize the from and to intersections
    def __getIntersectionForGeocode(geocode, id, eid1, eid2):
        """Get or synthesize intersection for geocode.

        If the geocode is at an intersection, just return the intersection;
        otherwise, synthesize a mid-block intersection.
        
        @param id Shared node ID at split
        @param eid1 Segment id for node-->id segment
        @param eid2 Segment id for id-->other_node segment
        @return An intersection object at at the split with a node ID of id
        
        """
        try:
            # Geocode is at an intersection--easy case
            i = geocode.intersection
        except AttributeError:
            # Geocode is in a segment--hard case
            # We have to generate an intersection in the middle of the segment
            # and add data to G
            #
            # Split the geocode's segment
            seg = geocode.segment
            num = geocode.address.number
            fn_seg, nt_seg = seg.splitAtNum(num, eid1, eid2, id)
            split_segs[eid1], split_segs[eid2] = fn_seg, nt_seg
            #
            # Create an intersection at the split
            st = seg.street
            st.number = num
            data = {'id': id,
                    'cross_streets': [st],
                    'lon_lat': nt_seg.linestring[0]}
            i = intersection.Intersection(data)
            #
            # Update G's nodes
            node_f_id, node_t_id = seg.node_f_id, seg.node_t_id
            __updateNodes(node_f_id, id, node_t_id, eid1, eid2)
            __updateNodes(node_t_id, id, node_f_id, eid2, eid1)
            #
            # Update G's edges
            eid = seg.id
            edges[eid1] = [fn_seg.getWeight()] + list(edges[eid][1:])
            edges[eid2] = [nt_seg.getWeight()] + list(edges[eid][1:])
        return i
    
    def __updateNodes(id1, id, id2, eid1, eid2):
        try:
            nodes[id1][id2]
        except KeyError:
            # id1 does NOT go to id2--nothing to do
            pass
        else:
            # id1 DOES go to id2
            if id not in nodes: nodes[id] = {}
            nodes[id1] = nodes[id1]
            nodes[id1][id] = eid1
            nodes[id][id2] = eid2
            # Override original connection so it won't be used
            nodes[id1][id2] = None  
            
    split_segs = {}
    nodes, edges = G['nodes'], G['edges']

    st = time.time()
    fint = __getIntersectionForGeocode(fcode, -1, -1, -2)
    messages.append('Time to get from intersection: %s' % (time.time() - st))

    st = time.time()
    tint = __getIntersectionForGeocode(tcode, -2, -3, -4)
    messages.append('Time to get to intersection: %s' % (time.time() - st))

    node_f_id, node_t_id = fint.id, tint.id

    
    ## Try to find a path
    st = time.time()
    try:
        V, E, W, w = sssp.findPath(G, node_f_id, node_t_id,
                                   weightFunction=mode.getEdgeWeight,
                                   heuristicFunction=None)
    except sssp.SingleSourceShortestPathsNoPathError:
        raise NoRouteError('Could not find a route')
    messages.append('Time to findPath: %s' % (time.time() - st))


    ## A path was found
    ## Get intersections and segments along path
    st = time.time()
    I = mode.getIntersectionsById(V)
    if I[0] is None: I[0] = fint   # When from is in a segment
    if I[-1] is None: I[-1] = tint # When to is in a segment
    messages.append('Time to fetch ints by ID %s' % (time.time()-st))

    st = time.time()
    S = mode.getSegmentsById(E)
    if S[0] is None: S[0] = split_segs[E[0]]    # When from is in a segment
    if S[-1] is None: S[-1] = split_segs[E[-1]] # When to is in a segment
    messages.append('Time to fetch segs by ID %s' % (time.time()-st))


    ## Convert route data to output format
    st = time.time()
    directions = makeDirections(I, S)
    messages.append('Time to make directions: %s' % (time.time() - st))
    route = {'from':       {'geocode': fcode, 'original': fr},
             'to':         {'geocode': tcode, 'original': to},
             'linestring': [],
             'directions': [],
             'directions_table': '',
             'distance':   {},
             'messages': []
             }
    route.update(directions)
    route['directions_table'] = _makeDirectionsTable(route)
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
    for (toi, s) in zip(I[1:], S):
        # Get the bearing of the segment--based on whether we are moving
        # toward its start or end
        # Assume moving fr => to
        frlonlat, tolonlat = s.linestring[0], s.linestring[1]
        e_frlonlat, e_tolonlat = s.linestring[-2], s.linestring[-1]
        sls = s.linestring

        if s.node_f_id == toi.id:
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
    ls_index = 0
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
                 'ls_index': ls_index,
                 'bikemode': [],
                 'distance': {'mi': '%.2f' % w,
                              'km': '%.2f' % (1.609344 * w),
                              'blocks': 0},
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
            toward = getDifferentNameInIntersection(st, toi)

            for var in ('turn', 'street', 'toward'): d[var] = eval(var)
            
            directions.append(d)
            d_count += 1

        # Save bearing if this segment is the last segment in a stretch
        try:
            if toi and W[s_count+1]:
                stretch_end_bearing = end_bearings[s_count] 
                stretch_end_name = st_str
        except IndexError:
            pass

        bm = str(s.bikemode)
        dbm = d['bikemode']
        if bm:
            try:
                if bm != dbm[-1]:
                    dbm.append(bm)
            except IndexError:
                dbm.append(bm)

        s_count += 1
        ls_index += len(s.linestring) - 1

    return {'directions': directions,
            'linestring': linestring,
            'distance': {'mi': mi, 'km': km, 'blocks': blocks}}


def getDifferentNameInIntersection(st, i):
    """Get street name from intersection that is different from street st."""
    for i_st in i.cross_streets:
        if st.name == i_st.name and st.type == i_st.type:
            continue
        else:
            return str(i_st)
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


def _makeDirectionsTable(route):
##    route = {'from':       {'geocode': fcode, 'original': fr},
##             'to':         {'geocode': tcode, 'original': to},
##             'linestring': [],
##             'directions': [],
##             'directions_table': '',
##             'distance':   {},
##             'messages': []
##            }

    distance = route['distance']['mi']
    fr = route['from']['geocode']
    fr_addr = fr.address
    fr_str = str(fr)
    to = route['to']['geocode']
    to_addr = to.address
    to_str = str(to)
    directions = route['directions']
    linestring = route['linestring']

    fr_point = linestring[0]
    to_point = linestring[-1]

    fr_addr = str(fr_addr).replace('\n', '<br/>')
    to_addr = str(to_addr).replace('\n', '<br/>')

    s_table = """
    <table id='summary'>
        <tr>
          <td class='start'>
            <h2><a href='javascript:void(0);' class='start'
                   onclick="map.showMapBlowup(%s)">Start</a>
            </h2>
          </td>
          <td class='start'>%s</a>
          </td>
        </tr>
        <tr>
          <td class='end'>
            <h2><a href='javascript:void(0);' class='end'
                   onclick="map.showMapBlowup(%s)">End</a>
            </h2>
          </td>
          <td class='end'>%s</td>
        </tr>
        <tr>
          <td class='total_distance'><h2>Distance</h2></td>
          <td>%s miles</td>
        </tr>
    </table>
    """ % (fr_point, fr_addr, to_point, to_addr, distance)

    d_table = """
    <!-- Directions -->
    <table id='directions'>%s</table>
    """

    d_row = """
    <tr>
      <td class='count %s'>
        <a href='javascript:void(0)'
           onclick="map.showMapBlowup(%s)">%s.</a>
      </td>
      <td class='direction %s'>%s</td>
    </tr>
    """
                      

    # Direction rows
    row_class = 'a'
    last = len(directions)
    i = 1
    tab = '&nbsp;&nbsp;&nbsp;&nbsp;'
    d_rows = []
    row_i = []
    for d in directions:
        turn = d['turn']
        street = d['street']
        toward = d['toward']
        jogs = d['jogs']
        ls_index = d['ls_index']
        mi = d['distance']['mi']

        row_i = []

        if turn == 'straight':
            prev = street[0]
            curr = street[1]
            row_i.append('%s <b>becomes</b> %s' % (prev, curr))
        else:
            if i == 1:
                cmd = 'Go'
                on = 'from'
                onto = '<b>%s</b>' % fr_str.split(',')[0]
            else:
                cmd = 'Turn'
                on = 'onto'
                onto = '<b>%s</b>' % street
            row_i.append('%s <b>%s</b> %s %s' % \
                             (cmd, turn, on, onto))

        if not toward:
            if i == last:
                toward = to_str.split(',')[0]
            else:
                toward = '?'
        row_i.append(' toward %s -- %smi' % (toward, mi))

	if d['bikemode']:
            row_i.append(' [%s]' % ', '.join([bm for bm in d['bikemode']]))

        if jogs:
            row_i.append('<br/>%sJogs...' % tab)
            for j in jogs:
                row_i.append('<br/>%s%s&middot; <i>%s</i> at %s' % \
                             (tab, tab, j['turn'], j['street']))

        d_rows.append(d_row % (row_class, linestring[ls_index], i,
                               row_class, ''.join(row_i)))
        del row_i[:]
        i += 1
        if row_class == 'a': row_class = 'b'
        else: row_class = 'a'

    last_row = d_row  % (row_class, linestring[-1], i, row_class,
                         '<b>End</b> at %s' % to_str)
    d_rows.append(last_row)
    
    d_table = d_table % ''.join([str(d) for d in d_rows])
    return ''.join((s_table, d_table))

    
if __name__ == '__main__':
    def print_key(key):
        for k in key:
            print k, 
            if type(key[k]) == type({}):
                print
                for l in key[k]:
                    print '\t', l, key[k][l]
            else: print key[k]
        print

    Qs = {'milwaukee':
          (('Puetz Rd & 51st St', '841 N Broadway St'),
           ('27th and lisbon', '35th and w north'),
           ('S 84th Street & Greenfield Ave', 'S 84th street & Lincoln Ave'),
           ('3150 lisbon', 'walnut & n 16th '),
           ('124th and county line, franklin', '3150 lisbon'),
           ('124th and county line, franklin', 'lon=-87.940407, lat=43.05321'),
           ('lon=-87.973645, lat=43.039615', 'lon=-87.978623, lat=43.036086'),
           ),
          'metro':
           (('633 n alberta', '44th and se stark'),
            ('-122.645488, 45.509475', 'sw hall & denney'),
           ),
          }
    
    tm = 'bike'

    for dm in ('milwaukee', 'metro'):
        qs = Qs[dm]
        for q in qs:
            try:
                r = get({'q': q, 'region': dm, 'tmode': tm})
            except MultipleMatchingAddressesError, e:
                print e.geocodes
            except Exception, e:
                raise
            else:
                D = r['directions']
                print r['from']['geocode']
                print r['to']['geocode']
                for d in D:
                    print '%s on %s toward %s -- %s mi [%s]' % \
                          (d['turn'],
                           d['street'],
                           d['toward'],
                           d['distance']['mi'],
                           d['bikemode'])
                print
                M = r['messages']
                for m in M:
                    print m
                print '----------------------------------------' \
                      '----------------------------------------'
            
        
