# Metro Mode
# 11/07/2005
import sys
sys.path += ['../../', '..']
from model import mode


class Mode(mode.Mode):
    def __init__(self):
        mode.Mode.__init__(self)
        self.g_file_name = './data/adjacency_matrix'

        self.tables.update({})
                            
        edge_fields = ('weight', 'stid', 'code', 'flags', 'upfrac', 'slope')
        self.indices = {}
        for i in range(len(edge_fields)): self.indices[edge_fields[i]] = i
        
        self.bikemodes = ['mu', 'mm', 'bl',
                          'lt', 'mt', 'ht',
                          'xx',
                          'pb', 'pm', 'up', 'ca']
        flag_names = ['gos', 'goe'] + self.bikemodes
        self.flags = {}
        i = 0
        for flag in flag_names:
            self.flags[flag] = 1 << i
            i += 1


    def createAdjacencyMatrix(self):
        # TODO: save adj. mat. to DB
        """Create this mode's adjacency matrix.

        For each vertex, u, build a sequence containing each vertex, v,
        adjacent to u and the edge that connects u to v.

        @return -- a compressed adjacency matrix for all intersections

        TODO: store G in DB instead of file?

        """
        from bycycle import db
        bdb = db.Db(self)
        Q = 'SELECT lid, frnid, tonid, code, flags, stid, len, upfrac, slope' \
            ' FROM %s WHERE code NOT IN (2000, 2100, 2200, 3220, 9000)' % \
            self.tables['edges']
        bdb.executeQuery(Q)
        R = bdb.fetchAllRows()
        segments = {}
        for r in R:
            for k in r: # convert all possible values to ints
                try: r[k] = int(r[k])
                except ValueError: pass
            segments[r['lid']] = r
        del R
        
        G = {'nodes': {}, 'edges': {}}
        nodes = G['nodes']
        edges = G['edges']

        for lid in segments:
            row = segments[lid]
            frnid, tonid = row['frnid'], row['tonid']
            flags = row['flags']
            gos = flags & self.flags['gos']
            goe = flags & self.flags['goe']
            entry = (row['len'], row['stid'], row['code'], flags,
                     row['upfrac'], row['slope'])
            edges[lid] = entry
            if gos:
                if not frnid in nodes: nodes[frnid] = {}
                nodes[frnid][tonid] = lid
            if goe:
                if not tonid in nodes: nodes[tonid] = {}
                nodes[tonid][frnid] = lid

        g_file = file(self.g_file_name, mode='wb')
        marshal.dump(G, g_file)
        g_file.close()
        return G
