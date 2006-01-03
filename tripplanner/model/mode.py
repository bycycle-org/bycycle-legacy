# Base Mode
# 11/07/2005
from pysqlite2 import dbapi2 as sqlite
from byCycle import install_path
from byCycle.lib import gis
import address, segment, intersection

class Mode(object):
    def __init__(self):
        edge_fields = ('weight', 'streetid', 'code')
        self.indices = {}
        for i in range(len(edge_fields)): self.indices[edge_fields[i]] = i
        
        self.tables = {'edges': 'streets',
                       'shapes': 'shapes',
                       'vertices': 'intersections',
                       'streetnames': 'streetnames',
                       'cities': 'cities',
                       'states': 'states'}

        # The number of digits after the implied decimal point of a lon or lat
        self.lon_lat_fraction_len = 6
        # What a lon or lat with an implied decimal point has to be multiplied
        # by to get the actual lon or lat
        self.lon_lat_exp = 10 ** -self.lon_lat_fraction_len

        # Set up the database connection
        self.data_path = '%stripplanner/model/%s/data/' % \
                         (install_path, self.dmode)
        self.db_path = self.data_path + 'db.db'
        self.matrix_path = self.data_path + 'matrix.pyc'
        self.connection = sqlite.connect(self.db_path)
        self.cursor = self.connection.cursor()
        def dict_factory(cursor, row):
            d = {}
            for idx, col in enumerate(cursor.description):
                d[col[0]] = row[idx]
            return d
        class DictCursor(sqlite.Cursor):
            def __init__(self, *args, **kwargs):
                sqlite.Cursor.__init__(self, *args, **kwargs)
                self.row_factory = dict_factory
        self.dict_cursor = self.connection.cursor(factory=DictCursor)


    def geocode(self, inaddr):
        import geocode
        return geocode.geocode(inaddr, self)


    def getAdjacencyMatrix(self):
        import marshal
        in_file = open(self.matrix_path, 'rb')
        G = marshal.load(in_file)
        in_file.close()
        return G


    #def getEdgeWeight(self, e, **kwargs):
    #    return 1

    
    def getHeuristic(self, e, d):
        try: self.lon_lat_goal
        except AttributeError:
            self.lon_lat_goal = (d[self.indices['lon']],
                                 d[self.indices['lat']])
        f = gis.getDistanceBetweenTwoPointsOnEarth
        return f(lon_a=e[self.indices['lon']],
                 lat_a=e[self.indices['lat']],
                 lon_b=self.lon_lat_goal[0],
                 lat_b=self.lon_lat_goal[1])


    # Intersection Methods ----------------------------------------------------

    def getIntersectionsById(self, nids):
        if not nids: return []
        intersections = []
        Q = 'SELECT * FROM %s WHERE nid IN (%s)' % \
            (self.tables['vertices'], ','.join([str(t) for t in nids]))
        ints = {}
        self.executeDict(Q)
        rows = self.fetchAllDict()
        if rows:
            # Index rows by nid
            irows = {}
            for row in rows: irows[row['nid']] = row

            # Pre-fetch segments and index by both fnode and tnode
            seg_rows = {}
            stnameids = {}
            nid_str = ','.join([str(i) for i in nids])
            Q = 'SELECT * FROM %s WHERE fnode IN (%s) OR tnode IN (%s)' % \
                (self.tables['edges'], nid_str, nid_str)
            self.executeDict(Q)
            for row in self.fetchAllDict():
                fnode, tnode = row['fnode'], row['tnode']
                if fnode in seg_rows: seg_rows[fnode].append(row)
                else: seg_rows[fnode] = [row]
                if tnode in seg_rows: seg_rows[tnode].append(row)
                else: seg_rows[tnode] = [row]
                stnameids[row['stnameid']] = 1
                
            # Pre-fetch full street names
            street_names = self.getRowsById('streetnames', stnameids.keys())
            streets = {}
            for stnameid in street_names:
                r = street_names[stnameid]
                st = address.Street(r['prefix'], r['name'],
                                    r['type'], r['suffix'])
                streets[stnameid] = st
                
            # Get intersections with the help of our pre-fetched data
            for nid in nids:
                try:
                    row = irows[nid]
                except KeyError:
                    intersections.append(None)
                    continue
                # Convert WKT point to Point
                geom = row['wkt_geometry']
                row['lon_lat'] = gis.importWktGeometry(geom)            
                # Get all segments that have the intersection at one end
                S = seg_rows[nid]
                # Get the cross streets
                cs = []
                seen_stnameids = {}
                for seg_row in S:
                    stnameid = seg_row['stnameid']
                    # Skip the segment if we've already seen a segment
                    # attached to this intersection that has the same
                    # street name (ID)
                    if stnameid in seen_stnameids: continue
                    else: seen_stnameids[stnameid] = 1
                    # Get segment street name
                    try: st = streets[stnameid]
                    except KeyError:
                        st = address.Street(name='unknown')
                        st.number = -1
                    else: 
                        fnode, tnode = seg_row['fnode'], seg_row['tnode']
                        fl, tl = seg_row['fraddl'], seg_row['toaddl']
                        fr, tr = seg_row['fraddr'], seg_row['toaddr']
                        # Determine the street number at the intersection
                        if fnode == nid:
                            if fl < tl: num = min(fl, fr)
                            else: num = max(fl, fr)
                        elif tnode == nid:
                            if fl < tl: num = min(tl, tr)
                            else: num = max(tl, tr)
                        st.number = num                        
                    cs.append(st)
                row['cross_streets'] = cs
                intersections.append(intersection.Intersection(row))        
        return intersections
        

    def getIntersectionById(self, nid):
        """Get intersection with specified ID.

        @param nid -- node ID
        @return -- an intersection object or None

        """
        return self.getIntersectionsById([nid])[0]


    def getIntersectionClosestToSTIDandNum(self, stnameid, num, lon_lat=None):
        """Get the intersection closest to the specified street address.

        @param stnameid -- the id of the addresses's street name
        @param num -- the street number of the address
        @param lon_lat -- the lon/lat of the address (if known)
        @return -- the closest intersection and the intersection accross from
                   it on the segment containing address

        """
        # First get the distance of the closest intersection (by street number)
        Q = "SELECT fnode, tnode, " \
            "ABS(fraddl-%s) AS fl, ABS(fraddr-%s) AS fr, " \
            "ABS(toaddl-%s) AS tl, ABS(toaddr-%s) AS tr, " \
            "LEAST(ABS(fraddl-%s), ABS(fraddr-%s), " \
            "      ABS(toaddl-%s), ABS(toaddr-%s)) AS m " \
            "FROM %s WHERE stnameid=%s ORDER BY m ASC LIMIT 1" % \
            (num, num, num, num, num, num, num, num,
             self.tables['edges'], stnameid)

        if not self.executeDict(Q): return None, None
        row = self.fetchRow()

        m, fl, fr, tl, tr = row["m"], row["fl"], row["fr"], row["tl"], row["tr"]
        if m in (fl, fr):
            nidc = row["fnode"]
            nida = row["tnode"]
        elif m in (tl, tr):
            nidc = row["tnode"]
            nida = row["fnode"]

        closest = self.getIntersectionById(nidc)
        acrossFromClosest = self.getIntersectionById(nida)

        # The closest might actually be the one that's "further" away in terms
        # street numbers
        if lon_lat:
            cll = closest.lon_lat
            afcll = acrossFromClosest.lon_lat
            if gis.getDistanceBetweenTwoPointsOnEarth(afcll, lon_lat) < \
                   gis.getDistanceBetweenTwoPointsOnEarth(cll, lon_lat):
                closest, acrossFromClosest = acrossFromClosest, closest

        return closest, acrossFromClosest


    def getIntersectionClosestToAddress(self, addr):
        """Find the intersection closest to a given location.

        @param addr -- The address to find the closest intersection to
        @return -- The intersection closest to addr
        """
        stnameids, num = self.getStreetIdsForAddress(addr=addr)
        stnameid, full_name = stnameids.popitem()
        i = self.getIntersectionClosestToSTIDandNum(stnameid, num, lon_lat)
        return i
 

    def getDistanceBetweenTwoIntersections(self, a, b):
        Q = "SELECT lon_lat FROM %s WHERE " \
            "nid=%s OR nid=%s" % (self.tables['vertices'], a.nid, b.nid)
        if not self.executeDict(Q): return None
        ll_a = gis.Point(self.fetchRow()["lon_lat"])
        ll_b = gis.Point(self.fetchRow()["lon_lat"])
        return gis.getDistanceBetweenTwoPointsOnEarth(ll_a, ll_b)


    def getLonLatByNid(self, nid):
        Q = "SELECT lon_lat FROM %s WHERE nid=%s" % \
            (self.tables['vertices'], nid)
        if not self.executeDict(Q): return None
        return gis.Point(self.fetchRow()["lon_lat"])


    # Segment Methods ---------------------------------------------------------

    def getSegmentsById(self, rowids):
        if not rowids: return []
        segments = []
        rowids_str = ','.join([str(t) for t in rowids])

        # Get segment records having a rowid in rowids
        Q = 'SELECT * FROM %s WHERE rowid IN (%s)' % \
            (self.tables['edges'], rowids_str)
        self.executeDict(Q)
        rows = self.fetchAllDict()

        if rows:
            # Index rows by rowid
            irows = {}
            for row in rows: irows[row['rowid']] = row

            # Add the extra attributes to the row
            Q = 'SELECT * FROM attrs WHERE rowid IN (%s)' % rowids_str
            self.executeDict(Q)
            arows = self.fetchAllDict()
            for i, arow in enumerate(arows):
                rowid = arow['rowid']
                irows[rowid].update(arow)
            del arows

            # Pre-fetch street names and cities
            stnameids, cityids = {}, {}
            for row in rows:
                stnameids[row['stnameid']] = 1
                cityids[row['cityidl']], cityids[row['cityidl']] = 1, 1
            street_names = self.getRowsById('streetnames', stnameids.keys())
            cities = self.getRowsById('cities', cityids.keys())

            # Get segments with the help of our pre-fetched data
            for rowid in rowids:
                try:
                    row = irows[rowid]
                except KeyError:
                    segments.append(None)
                    continue
                # Get street name components, removing the rowid entry first
                street = street_names[row['stnameid']]
                try: del street['rowid']
                except KeyError: pass
                row.update(street)
                row['street'] = address.Street(row['prefix'], row['name'],
                                               row['type'], row['suffix'])
                # Get city names for each side
                row['cityl'] = cities[row['cityidl']]['city']
                row['cityr'] = cities[row['cityidr']]['city']
                # Convert WKT linestring to list of points
                geom = row['wkt_geometry']
                row['linestring'] = gis.importWktGeometry(geom)
                # Append current segment to output list
                segments.append(segment.Segment(row))
        return segments

    
    def getSegmentById(self, rowid):
        """Get a segment with specified ID.

        @param rowid -- segment ID
        @return -- a segment object or None

        """
        return self.getSegmentsById([rowid])[0]


    def getSegmentByNumStreetId(self, num, stnameid):
        Q = "SELECT rowid FROM %s " \
            "WHERE stnameid=%s AND " \
            "%s BETWEEN LEAST(fraddl,fraddr) AND GREATEST(toaddl,toaddr)" % \
            (self.tables['edges'], stnameid, num)
        if not self.executeDict(Q):
            Q = "SELECT rowid FROM %s " \
                "WHERE stnameid=%s AND " \
                "%s BETWEEN FLOOR(LEAST(fraddl,fraddr)/100)*100 AND " \
                "CEILING(GREATEST(toaddl,toaddr)/100)*100" % \
                (self.tables['edges'], stnameid, num)
            if not self.executeDict(Q): return None
        return self.getSegmentById(self.fetchRow()["rowid"])


    def getSegmentByNids(self, fnode, tnode):
        Q = "SELECT rowid FROM %s WHERE " \
            "(fnode=%s AND tnode=%s) OR (fnode=%s AND tnode=%s)" % \
            (self.tables['edges'], fnode, tnode, tnode, fnode)
        if not self.executeDict(Q): return None
        return self.getSegmentById(self.fetchRow()["rowid"])


    # Utility Methods ---------------------------------------------------------

    def getRowsById(self, table, rowids, dict=True):
        """Fetch from table rows with row IDs. Return dict of {rowids=>row}."""
        result = {}
        Q = 'SELECT * FROM %s WHERE rowid IN (%s)' % \
            (table, ','.join([str(i) for i in rowids]))
        if dict:
            self.executeDict(Q)
            for r in self.fetchAllDict(): result[r['rowid']] = r
        else:
            self.execute(Q)
            for r in self.fetchAll(): result[r[0]] = r            
        return result

    def escapeString(self, string):
        """MySQL-escape a string."""
        return MySQLdb.escape_string(string)

    def escapeList(self, list):
        """MySQL-escape a list of strings."""
        new_list = []
        for string in list:
            if string: new_list.append(MySQLdb.escape_string(string))
            else: new_list.append(None)
        return new_list

    def sanitizeString(self, string):
        return MySQLdb.escape_string(' '.join(string.split()).lower())

    def sanitizeList(self, string):
        new_list = []
        for string in list:
            if string:
                new_list.append(MySQLdb.escape_string \
                                (' '.join(string.split()).lower()))
            else: new_list.append(None)
        return new_list

    def execute(self, Q):
        try: return self.cursor.execute(Q)
        except Exception, e:
            print Q
            print e
            raise

    def executeDict(self, Q):
        try: return self.dict_cursor.execute(Q)
        except Exception, e:
            print Q
            print e
            raise

    def executeMany(self, Q, values_list):
        try: return self.cursor.executemany(Q, values_list)
        except _mysql_exceptions.MySQLError, e: raise
        except: raise

    def getTableUpdateTime(self, table):
        Q = "show table status like '%s'" % table
        self.executeDict(Q)
        return self.fetchRow()["Update_time"]

    def fetchRow(self): return self.cursor.fetchone()
    def fetchRowDict(self): return self.dict_cursor.fetchone()
    def fetchAll(self): return self.cursor.fetchall()
    def fetchAllDict(self): return self.dict_cursor.fetchall()

    def commit(self): self.connection.commit()


if __name__ == "__main__":
    pass
