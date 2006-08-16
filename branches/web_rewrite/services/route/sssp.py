"""$Id$

Description goes here.

Copyright (C) 2006 Wyatt Baldwin, byCycle.org <wyatt@bycycle.org>

All rights reserved.

TERMS AND CONDITIONS FOR USE, MODIFICATION, DISTRIBUTION

1. The software may be used and modified by individuals for noncommercial, 
private use.

2. The software may not be used for any commercial purpose.

3. The software may not be made available as a service to the public or within 
any organization.

4. The software may not be redistributed.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND 
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED 
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE 
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR 
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES 
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; 
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON 
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT 
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS 
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
# Single-source Shortest Paths
#
# TODO:
# Write a function to do All Pairs Shortest Paths

infinity = 2147483647

class SingleSourceShortestPathsError(Exception):
    pass

class SingleSourceShortestPathsNoPathError(SingleSourceShortestPathsError):
    pass


def singleSourceShortestPaths(G, s, d=None,
                              weightFunction=None,
                              heuristicFunction=None):
    """Dijkstra with a few twists

    Args:
    G -- adjacency matrix
    (# nodes
     (((v, e), (v, e), (v, e)),
      ((v, e), (v, e)),
      .
      .
      .
     ),
     # edges
     ((a, b, c, d),
      (a, b, c, d),
      .
      .
      .
     )
    )

         edges _must_ contain the weight entry first; it may also contain
         other attributes of the edge. These other attributes can be used to
         determine a different weight for the edge.
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
    
    nodes, edges = G[0], G[1]

    count = 0
    while open:
        count += 1
        # In the nodes remaining in G that have a known weight from s,
        # find the node, u, that currently has the shortest path from s
        w_of_s_to_u, u = heapq.heappop(open)

        # Get the attributes of the segment crossed to get to u
        try:
            prev_e_attrs = P[u][2]
        except KeyError:
            prev_e_attrs = None
            
        # Get nodes adjacent to u...
        try:
            A = nodes[u]
        except KeyError:
            # We'll get here upon reaching a node with no outgoing edges
            continue

        # ...and explore the edges that connect u to those nodes, updating
        # the weight of the shortest paths to any or all of those nodes as
        # necessary. v is the node across the current edge from u.
        for v in A:
            e = A[v]

            # e is set to None in G to indicate we don't want to use a segment
            # in one or the other or both directions
            try:
                e_attrs = edges[e]
            except KeyError:
                continue

            # Get the weight of the edge running from u to v
            try:
                w_of_e = weightFunction(v, e_attrs, prev_e_attrs)
            except TypeError:
                w_of_e = e_attrs[0]

            # Weight of s to u plus the weight of u to v across e--this is *a*
            # weight from s to v that may or may not be less than the current
            # known weight to v
            w_of_s_to_u_plus_w_of_e = w_of_s_to_u + w_of_e

            # When there is a heuristic function, we use a "guess-timated"
            # weight, which is the normal weight plus some other heuristic
            # weight from v to d that is calculated so as to keep us moving
            # in the right direction (generally more toward the goal instead
            # of away from it).
            #try:
            #    w_of_s_to_u_plus_w_of_e += heuristicFunction(e)
            #except TypeError:
            #    pass
                
            # Get the weight of the path from s to v, if known
            try:
                w_of_s_to_v = W[v]
            except KeyError:
                # If no path to v had been found previously, v's path-weight 
                # from s will have been previously unknown (infinity); 
                # since we have just found a path from s to v, we need to add
                # v's path-weight from s to the list of nodes with known
                # weights from s
                w_of_s_to_v = infinity  # note: this gets used below
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

            # If a destination node was specified and we reached it, we're done
            if v == d:
                open = None
                break

    # There is no path from start to d when the weight to d is infinite
    if W[d] == infinity:
        raise SingleSourceShortestPathsNoPathError

    return P, W


def extractShortestPathFromPredecessorList(P, d):
    """Extract ordered lists of nodes, edges, weights from predecessor list.

    @param P Predecessor list {u: (v, e), ...}
             u's predecessor is v via segment e
    @param d Destination node ID. We find the path from

    @return
    V A list of the node IDs on the lightest path from start to d
    E A list of the edge IDs on the lightest path from start to d
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


def findPath(G, s, d, weightFunction=None, heuristicFunction=None):
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
    P, W = singleSourceShortestPaths(G, s, d,
                                     weightFunction=weightFunction,
                                     heuristicFunction=heuristicFunction)
    return extractShortestPathFromPredecessorList(P, d)
