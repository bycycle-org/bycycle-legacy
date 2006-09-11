"""$Id$

Route Service Module (28 Dec 2004)

Copyright (C) 2006 Wyatt Baldwin, byCycle.org <wyatt@bycycle.org>. All rights 
reserved. Please see the LICENSE file included in the distribution. The
license is also available online at http://bycycle.org/tripplanner/license.txt
or by writing to license@bycycle.org.

"""
import time
from byCycle.lib import gis
from byCycle.services import excs
from byCycle.model import address, intersection
from byCycle.services import geocode
import sssp


class RouteError(excs.ByCycleError):
    def __init__(self, desc='Route Error'):
        excs.ByCycleError.__init__(self, desc)
    def __str__(self):
        return self.description

class NoRouteError(RouteError):
    def __init__(self, desc='No Route Error'):
        RouteError.__init__(self, desc=desc)

class MultipleMatchingAddressesError(RouteError):
    def __init__(self, desc='Multiple Matches Found',
                 start_choices=None, end_choices=None):
        print start_choices
        print end_choices
        self.start_choices = start_choices
        self.end_choices = end_choices
        RouteError.__init__(self, desc=desc)


def get(q, region='', tmode='bicycle', pref='', return_messages=False):
    """Get a route for the addresses in the waypoint list q.
    
    @param region: Geographic region to find the input addresses and route in
    @type region: string
    @param tmode The travel mode (currently only 'bicycle' is supported)
    @type tmode: string
    @param q A list of addresses (currently only 2 supported)
    @type q: sequence<string>
    @param pref:  User's route preference
    @type pref: string

    @return: Route
    @rtype: dict
    
    @raise excs.InputError: No start and/or end address
    @raise MultipleMatchingAddressesError: Multiple geocode matches for start 
      and/or end address
    @raise NoRouteError: No route found between start and end addresses

    TODO: 
      - Make less monolithic
      - Make logging & timing orthogonal to get (it's all cluttered up with
        logging & timing statements
      - Support more than 2 waypoints
      
    """
    st_tot = time.time()
    messages, errors = [], []

    #-- Do basic input check
    
    if not q:
        errors.append('Please enter start and end addresses')
    else:
        try:
            start = q[0].strip()
            if not start:
                raise IndexError
        except IndexError:
            errors.append('Please enter a start address')
        try:
            end = q[1].strip()
            if not end:
                raise IndexError
        except IndexError:
            errors.append('Please enter an end address')

    # Let multiple input errors fall through to here
    if errors:
        raise excs.InputError(errors)

    #-- Get geocodes matching start and end addresses
    
    start_choices = {'choices': [], 'original': start}
    end_choices = {'choices': [], 'original': end}
             
    st = time.time()
    try:
        start_geocodes = geocode.get(q=start, region=region)
    except geocode.AddressNotFoundError, e:
        errors.append(e.description)
    except geocode.MultipleMatchingAddressesError, e:
        start_choices['choices'] = e.geocodes
    messages.append('Time to get from address: %s' % (time.time() - st))
    
    st = time.time()
    try:
        end_geocodes = geocode.get(q=end, region=region)
    except geocode.AddressNotFoundError, e:
        errors.append(e.description)
    except geocode.MultipleMatchingAddressesError, e:
        end_choices['choices'] = e.geocodes
    messages.append('Time to get to address: %s' % (time.time() - st))

    # Let multiple multiple-match errors fall through to here
    if start_choices['choices'] or end_choices['choices']:
        if not start_choices['choices']:
            start_choices = None
        if not end_choices['choices']:
            end_choices = None        
        raise MultipleMatchingAddressesError(start_choices=start_choices,
                                             end_choices=end_choices)

    # Precise (enough) addresses were entered
    start_geocode, end_geocode = start_geocodes[0], end_geocodes[0]

    # TODO: Make this check actually work
    if start_geocode == end_geocode:
        raise excs.InputError('From and To addresses appear to be the same')


    # The mode is a combination of the data/travel modes
    st = time.time()
    path = 'byCycle.model.%s.%s'
    module = __import__(path % (region, tmode), globals(), locals(), [''])
    mode = module.Mode(pref=pref)
    messages.append('Time to instantiate mode: %s' % (time.time() - st))

    #-- Made it through that maze--now fetch the main adjacency matrix, G
    
    st = time.time()
    G = mode.getAdjacencyMatrix()
    if not G:
        raise NoRouteError('Graph is empty')
    messages.append('Time to get G: %s' % (time.time() - st))

    #-- Get or synthesize the start and end intersections
    
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
                    'xy': nt_seg.linestring[0]}
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
    fint = __getIntersectionForGeocode(start_geocode, -1, -1, -2)
    messages.append('Time to get from intersection: %s' % (time.time() - st))

    st = time.time()
    tint = __getIntersectionForGeocode(end_geocode, -2, -3, -4)
    messages.append('Time to get to intersection: %s' % (time.time() - st))

    node_f_id, node_t_id = fint.id, tint.id
    
    #-- Try to find a path
    
    st = time.time()
    try:
        V, E, W, w = sssp.findPath(G, node_f_id, node_t_id,
                                   weightFunction=mode.getEdgeWeight,
                                   heuristicFunction=None)
    except sssp.SingleSourceShortestPathsNoPathError:
        raise NoRouteError('Unable to find a route from "%s" to "%s"' % \
                           (str(start_geocode).replace('\n', ', '),
                            str(end_geocode).replace('\n', ', ')))
    messages.append('Time to findPath: %s' % (time.time() - st))

    #-- A path was found
    
    # Get intersections and segments along path
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

    #-- Convert route data to output format
    
    st = time.time()
    directions = makeDirections(I, S)
    messages.append('Time to make directions: %s' % (time.time() - st))
    route = {
        'start': {'geocode': start_geocode,
               'original': start,
               },
        'end': {'geocode': end_geocode,
               'original': end,
               },
        'linestring': [],
        'directions': [],
        'distance': {},
        'messages': [],
        }
    route.update(directions)
    if return_messages:
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
        sls = s.linestring
        if s.node_f_id == toi.id:
            # Moving to => start
            sls.reverse()
        frlonlat, tolonlat = sls[0], sls[1]
        e_frlonlat, e_tolonlat = sls[-2], sls[-1]

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
    stretch_start_x = 0
    streets = []
    jogs = []
    for seg_x, s in enumerate(S):
        st = address.Street(s.prefix, s.name, s.sttype, s.suffix)
        streets.append(st)  # save for later
        name_type = '%s %s' % (s.name, s.sttype)

        try:
            next_s = S[seg_x + 1]
        except IndexError:
            next_name_type = None
        else:
            next_name_type = '%s %s' % (next_s.name, next_s.sttype)
        
        if name_type == prev_name_type:
            W[stretch_start_x] += W[seg_x]
            W[seg_x] = None
            prev_name_type = name_type
        # Check for jog
        elif prev_name_type and \
                 W[seg_x] < .05 and name_type != prev_name_type and \
                 next_name_type == prev_name_type:
            W[stretch_start_x] += W[seg_x]
            W[seg_x] = None
            turn = calculateWayToTurn(bearings[seg_x], end_bearings[seg_x - 1])
            jogs[-1].append({'turn': turn, 'street': str(st)})
        else:
            # Start of a new stretch (i.e., a new direction)
            stretch_start_x = seg_x
            prev_name_type = name_type
            jogs.append([])


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
        
        if w is not None:
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

            for var in ('turn', 'street', 'toward'):
                d[var] = eval(var)
            
            directions.append(d)
            d_count += 1

        # Save bearing if this segment is the last segment in a stretch
        try:
            if toi and W[s_count+1]:
                stretch_end_bearing = end_bearings[s_count] 
                stretch_end_name = st_str
        except IndexError:
            pass

        # Add segment's bikemode to list of bikemodes for current stretch
        try:
            bm = str(s.bikemode)
        except AttributeError:
            pass
        else:
            if bm:
                try:
                    # Only record changes in bikemode
                    if bm != d['bikemode'][-1]:
                        d['bikemode'].append(bm)
                except IndexError:
                    # First segment in stretch with a bikemode
                    d['bikemode'].append(bm)

        s_count += 1
        ls_index += len(s.linestring) - 1

    return {'directions': directions,
            'linestring': linestring,
            'distance': {'mi': mi, 'km': km, 'blocks': blocks}}


def getDifferentNameInIntersection(st, i):
    """Get street name from intersection that is different from street st."""
    for i_st in i.cross_streets:
        if st.name == i_st.name and st.sttype == i_st.sttype:
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


if __name__ == '__main__':
    import sys

    def print_key(key):
        for k in key:
            print k, 
            if type(key[k]) == type({}):
                print
                for l in key[k]:
                    print '\t', l, key[k][l]
            else: print key[k]
        print

    try:
        region, q = sys.argv[1].split(',')
    except IndexError:
        Qs = {'milwaukeewi':
              (('Puetz Rd & 51st St', '841 N Broadway St'),
               ('27th and lisbon', '35th and w north'),
               ('S 84th Street & Greenfield Ave',
                'S 84th street & Lincoln Ave'),
               ('3150 lisbon', 'walnut & n 16th '),
               ('124th and county line, franklin', '3150 lisbon'),
               ('124th and county line, franklin',
                'x=-87.940407, y=43.05321'),
               ('x=-87.973645, y=43.039615',
                'x=-87.978623, y=43.036086'),
               ),
              'portlandor':
               (('x=-122.668104, y=45.523127', '4807 se kelly'),
                ('x=-122.67334,y=45.621662', '8220 N Denver Ave'),
                ('633 n alberta', '4807 se kelly'),
                ('sw hall & denney', '44th and se stark'),
                ('-122.645488, 45.509475', 'sw hall & denney'),
               ),
              }
    else:
        q = q.split(' to ')
        Qs = {region: (q,)}


    for dm in Qs:
        qs = Qs[dm]
        for q in qs:
            try:
                st = time.time()
                r = get(return_messages=1, region=dm, q=q)
                et = time.time() - st
            except MultipleMatchingAddressesError, e:
                print e.route
            except NoRouteError, e:
                print e
            #except Exception, e:
            #    print e
            else:
                D = r['directions']
                print r['start']['geocode']
                print r['end']['geocode']
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
                print 'Took %.2f' % et
                print '----------------------------------------' \
                      '----------------------------------------'
