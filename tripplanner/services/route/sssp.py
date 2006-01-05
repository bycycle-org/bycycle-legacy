# Single-source Shortest Paths
#
# TODO:
# Write a function to do All Pairs Shortest Paths

infinity = 2147483647

class SingleSourceShortestPathsError(Exception):
    pass

class SingleSourceShortestPathsNoPathError(SingleSourceShortestPathsError):
    pass


def singleSourceShortestPaths(G, H, s, d=None,
                              weightFunction=None,
                              heuristicFunction=None):
    """Dijkstra with a few twists

    Args:
    G -- adjacency matrix {'nodes': {v: {u: e,...}, ...},
                           'edges': {e: (e.weight,e.attr1,e.attr2,...), ...}}
         edges _must_ contain the weight entry first; it may also contain 
         other attributes of the edge. These other attributes can be used to
         determine a different weight for the edge.
    H -- an auxillary adjacency matrix. It is used to add segments to G
         without modifying it. Entries in H override entries in G.
    s -- start node ID
    d -- destination node ID
         If d is None (default) the algorithm is run normally
         If d has a value, the algorithm is stopped when a path to
         d has been found
    weightFunction -- function to apply to each edge to modify its base weight
    heuristicFunction -- function to apply at each iteration to help the
                         poor dumb machine try to move toward the destination
                         instead of just any and every which way

    Return:
    P -- predecessor list {v => (u, e), ...}
    W -- the weights of the paths from s to all v in G

    """
    # TODO: use Fibonnaci heap instead of built-in!
    import heapq

    # weights of shortest paths from s to all v (ID of v => w)
    W = {s: 0, d: infinity}
    # partially sorted list of nodes w/ known weights from s
    open = [(0, s)]
    # predecessor of each node that has shortest path from s
    P = {}
    # list of all edges already crossed, in order
    E = []       
    
    G_nodes, G_edges = G["nodes"], G["edges"]
    H_nodes, H_edges = H["nodes"], H["edges"]

    count = 0
    while open:
        count += 1
        # In the nodes remaining in G that have a known weight from s,
        # find the node, u, that currently has the shortest path from s
        w_s_to_u, u = heapq.heappop(open)

        # Append the attrs of the segment crossed to get to 
        if weightFunction:
            try:
                prev_e_attrs = P[u][2]
            except KeyError:
                prev_e_attrs = None

        # Get nodes adjacent to u (preferring matrix H)...
        try:
            A = H_nodes[u]
        except KeyError:
            try:
                A = G_nodes[u]
            except KeyError:
                # We'll get here upon reaching a node with no outgoing edges
                continue

        # ... and explore the edges that connect u to those nodes, updating
        # the weight of the shortest paths to any or all of those nodes as
        # necessary. v is the name of the node across the current edge from u. 
        #print
        #print "Currently sitting at:", u, "<br>"
        #print "Exploring surrounding nodes...", "<br>"
        for v in A:
            e = A[v]

            # e can set to None in H to indicate we don't want to use a segment
            # in one or the other or both directions
            if e is None: continue

            try:
                e_attrs = H_edges[e]
            except KeyError:
                e_attrs = G_edges[e]

            # Get the weight of the edge running from u to v
            if weightFunction:
                w_of_e = weightFunction(e_attrs, prev_e_attrs)
            else:
                w_of_e = e_attrs[0]

            # Weight of s to u plus the weight of u to v across e--this is *a*
            # weight from s to v that may or may not be less than the current
            # known weight to v
            w_of_s_to_u_plus_w_of_e = w_s_to_u + w_of_e

            # When there is a heuristic function, we use a "guess-timated"
            # weight, which is the normal weight plus some other heuristic
            # weight from v to d that is calculated so as to keep us moving
            # in the right direction (generally more toward the goal instead
            # of away from it).
            if heuristicFunction and d_edge:
                w_of_s_to_u_plus_w_of_e += heuristicFunction(e, d_edge)

            # Get the weight of the path from s to v, if known
            try:
                w_of_s_to_v = W[v]
            except KeyError:
                # If no path to v had been found previously, v's path-weight 
                # from s will have been previously unknown (infinity); 
                # since we have just found a path from s to v, we need to add
                # v's path-weight from s to the list of  nodes with known
                # weights from s
                w_of_s_to_v = infinity
                heapq.heappush(open, (w_of_s_to_u_plus_w_of_e, v))

            # If the current known weight from s to v is greater than the new
            # weight we just found (weight of s to u plus weight of u to v
            # across e), update v's weight in the weight list and update v's
            # predecessor in the predecessor list (it's now u)
            if w_of_s_to_v > w_of_s_to_u_plus_w_of_e:
                W[v] = w_of_s_to_u_plus_w_of_e
                # u is v's predecessor node. e is the ID of the edge running
                # from u to v on the shortest known path from s to v. We
                # include the edge's other attributes too.
                P[v] = (u, e, e_attrs)

        # If a destination node was specified and we've found it, we're done
        if u == d: break

    # There is no path from start to d when the weight to d is infinite
    if W[d] == infinity:
        raise SingleSourceShortestPathsNoPathError

    return P, W


def extractShortestPathFromPredecessorList(P, d, ):
    """Extract ordered lists of nodes, edges, weights from predecessor list.

    @param P Predecessor list {u: (v, e), ...}
             u's predecessor is v via segment e
    @param d Destination node ID. We find the path from

    @return
    V A list of the node IDs on the lightest path from start to d
    V A list of the edge IDs on the lightest path from start to d
    W A list of the weights of the segments on the lightest path from s to d
    w The total weight of the segments with IDs in E

    """
    V = [] # the nodes on the shortest path from s to d
    E = [] # the edges on the shortest path from s to d
    W = [] # the weights of the segments on the shortest route from s to d

    u = d
    while u in P:
        predecessor_data = P[u]
        e = predecessor_data[1]
        attrs = predecessor_data[2]
        V.append(u)
        E.append(e)
        W.append(attrs[0])
        u = predecessor_data[0]

    V.append(u)  # Insert ID of starting node
    V.reverse(); E.reverse(); W.reverse()
    w = reduce(lambda x, y: x + y, W)

    return V, E, W, w


def findPath(G, H, s, d, weightFunction=None, heuristicFunction=None):
    """Find the shortest path from s to d in G.

    This function just combines finding the predecessor list with extracting
    the nodes from that list in the proper (path) order, 'cause what you want
    is probably that ordered list.

    @param G Graph
    @param s Start node ID
    @param d Destination node ID
    @return -- V, E, W, w, which are the nodes, edges, weights and total
               weight of the route from u to v

    """
    P, W = singleSourceShortestPaths(G, H, s, d,
                                     weightFunction=weightFunction,
                                     heuristicFunction=heuristicFunction)
    return extractShortestPathFromPredecessorList(P, d)


