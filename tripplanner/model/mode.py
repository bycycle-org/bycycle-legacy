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
        
        self.tables = {'edges': 'layer_street',
                       'street_attrs': 'attr_street',
                       'vertices': 'layer_node',
                       'streetnames': 'streetname',
                       'cities': 'city',
                       'states': 'state'}

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

    def getIntersectionsById(self, ids):
        if not ids: return []
        intersections = []
        id_str = ','.join([str(i) for i in ids])
        Q = 'SELECT id_node_f, id_node_t, addr_f, addr_t, ix_streetname, ' \
            'wkt_geometry ' \
            'FROM %s ' \
            'WHERE id_node_f IN (%s) OR id_node_t IN (%s)' % \
            (self.tables['edges'], id_str, id_str)
        self.executeDict(Q)
        rows = self.fetchAllDict()
        if rows:
            # Pre-fetch segments and index by both id_node_f and id_node_t
            seg_rows = {}
            ix_streetnames = {}
            for row in rows:
                id_node_f, id_node_t = row['id_node_f'], row['id_node_t']
                if id_node_f in seg_rows: seg_rows[id_node_f].append(row)
                else: seg_rows[id_node_f] = [row]
                if id_node_t in seg_rows: seg_rows[id_node_t].append(row)
                else: seg_rows[id_node_t] = [row]
                ix_streetnames[row['ix_streetname']] = 1
                
            # Pre-fetch full street names
            streetnames = self.getRowsById(self.tables['streetnames'],
                                           ix_streetnames.keys())
            streets = {}
            for ix_streetname in streetnames:
                r = streetnames[ix_streetname]
                st = address.Street(r['prefix'], r['name'],
                                    r['type'], r['suffix'])
                streets[ix_streetname] = st
                
            # Get intersections with the help of our pre-fetched data
            for id in ids:
                data = {}
                try:
                    row = seg_rows[id][0]
                except KeyError:
                    intersections.append(None)
                    continue
                # Get segment linestring and point at id end
                linestring = gis.importWktGeometry(row['wkt_geometry'])
                id_node_f, id_node_t =  row['id_node_f'],  row['id_node_t']
                if id == id_node_f:
                    data['id'] = id_node_f
                    data['lon_lat'] = linestring[0]
                elif id == id_node_t:
                    data['id'] = id_node_t
                    data['lon_lat'] = linestring[-1]
                # Get all segments that have the intersection at one end
                S = seg_rows[id]
                # Get the cross streets
                cs = []
                seen_ix_streetnames = {}
                for seg_row in S:
                    ix_streetname = seg_row['ix_streetname']
                    # Skip the segment if we've already seen a segment
                    # attached to this intersection that has the same
                    # street name (ID)
                    if ix_streetname in seen_ix_streetnames: continue
                    else: seen_ix_streetnames[ix_streetname] = 1
                    # Get segment street name
                    try: st = streets[ix_streetname]
                    except KeyError:
                        st = address.Street(name='unknown')
                        st.number = -1
                    else: 
                        id_node_f = seg_row['id_node_f']
                        id_node_t = seg_row['id_node_t']
                        addr_f, addr_t = seg_row['addr_f'], seg_row['addr_t']
                        # Determine the street number at the intersection
                        if id_node_f == id:
                            num = addr_f
                        elif id_node_t == id:
                            num = addr_t
                        st.number = num                        
                    cs.append(st)
                data['cross_streets'] = cs
                intersections.append(intersection.Intersection(data))        
        return intersections
        

    def getIntersectionById(self, id):
        """Get intersection with specified ID.

        @param id -- node ID
        @return -- an intersection object or None

        """
        return self.getIntersectionsById([id])[0]


    def getIntersectionClosestToSTIDandNum(self, ix_streetname, num, lon_lat=None):
        """Get the intersection closest to the specified street address.

        @param ix_streetname -- the id of the addresses's street name
        @param num -- the street number of the address
        @param lon_lat -- the lon/lat of the address (if known)
        @return -- the closest intersection and the intersection accross from
                   it on the segment containing address

        """
        # First get the distance of the closest intersection (by street number)
        Q = "SELECT id_node_f, id_node_t, " \
            "ABS(fraddl-%s) AS fl, ABS(fraddr-%s) AS fr, " \
            "ABS(toaddl-%s) AS tl, ABS(toaddr-%s) AS tr, " \
            "LEAST(ABS(fraddl-%s), ABS(fraddr-%s), " \
            "      ABS(toaddl-%s), ABS(toaddr-%s)) AS m " \
            "FROM %s WHERE ix_streetname=%s ORDER BY m ASC LIMIT 1" % \
            (num, num, num, num, num, num, num, num,
             self.tables['edges'], ix_streetname)

        if not self.executeDict(Q): return None, None
        row = self.fetchRow()

        m, fl, fr, tl, tr = row["m"], row["fl"], row["fr"], row["tl"], row["tr"]
        if m in (fl, fr):
            idc = row["id_node_f"]
            ida = row["id_node_t"]
        elif m in (tl, tr):
            idc = row["id_node_t"]
            ida = row["id_node_f"]

        closest = self.getIntersectionById(idc)
        acrossFromClosest = self.getIntersectionById(ida)

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
        ix_streetnames, num = self.getStreetIdsForAddress(addr=addr)
        ix_streetname, full_name = ix_streetnames.popitem()
        i = self.getIntersectionClosestToSTIDandNum(ix_streetname, num, lon_lat)
        return i
 

    def getDistanceBetweenTwoIntersections(self, a, b):
        Q = "SELECT lon_lat FROM %s WHERE " \
            "id=%s OR id=%s" % (self.tables['vertices'], a.id, b.id)
        if not self.executeDict(Q): return None
        ll_a = gis.Point(self.fetchRow()["lon_lat"])
        ll_b = gis.Point(self.fetchRow()["lon_lat"])
        return gis.getDistanceBetweenTwoPointsOnEarth(ll_a, ll_b)


    def getLonLatById(self, id):
        Q = "SELECT lon_lat FROM %s WHERE id=%s" % \
            (self.tables['vertices'], id)
        if not self.executeDict(Q): return None
        return gis.Point(self.fetchRow()["lon_lat"])


    # Segment Methods ---------------------------------------------------------

    def getSegmentsById(self, ixs):
        if not ixs: return []
        segments = []
        ixs_str = ','.join([str(t) for t in ixs])

        # Get segments with ix in ixs
        Q = 'SELECT * FROM %s WHERE ix IN (%s)' % \
            (self.tables['edges'], ixs_str)
        self.executeDict(Q)
        rows = self.fetchAllDict()

        if rows:
            # Index rows by ix
            irows = {}
            for row in rows: irows[row['ix']] = row

            # Add the extra attributes to the row
            Q = 'SELECT * FROM attr_street WHERE ix IN (%s)' % ixs_str
            self.executeDict(Q)
            arows = self.fetchAllDict()
            for i, arow in enumerate(arows):
                ix = arow['ix']
                irows[ix].update(arow)
            del arows

            # Pre-fetch street names and cities
            ix_streetnames, cityids = {}, {}
            for row in rows:
                ix_streetnames[row['ix_streetname']] = 1
                cityids[row['ix_city_l']], cityids[row['ix_city_l']] = 1, 1
            street_names = self.getRowsById(self.tables['streetnames'], 
                                            ix_streetnames.keys())
            cities = self.getRowsById(self.tables['cities'], cityids.keys())

            # Get segments with the help of our pre-fetched data
            for ix in ixs:
                try:
                    row = irows[ix]
                except KeyError:
                    segments.append(None)
                    continue
                # Get street name components, removing the ix entry first
                street = street_names[row['ix_streetname']]
                try: del street['ix']
                except KeyError: pass
                row.update(street)
                row['street'] = address.Street(row['prefix'], row['name'],
                                               row['type'], row['suffix'])
                # Get city names for each side
                row['city_l'] = cities[row['ix_city_l']]['city']
                row['city_r'] = cities[row['ix_city_r']]['city']
                # Convert WKT linestring to list of points
                geom = row['wkt_geometry']
                row['linestring'] = gis.importWktGeometry(geom)
                # Append current segment to output list
                segments.append(segment.Segment(row))
        return segments

    
    def getSegmentById(self, ix):
        """Get a segment with specified ID.

        @param ix -- segment ID
        @return -- a segment object or None

        """
        return self.getSegmentsById([ix])[0]


    def getSegmentByNumStreetId(self, num, ix_streetname):
        Q = "SELECT ix FROM %s " \
            "WHERE ix_streetname=%s AND " \
            "%s BETWEEN LEAST(fraddl,fraddr) AND GREATEST(toaddl,toaddr)" % \
            (self.tables['edges'], ix_streetname, num)
        if not self.executeDict(Q):
            Q = "SELECT ix FROM %s " \
                "WHERE ix_streetname=%s AND " \
                "%s BETWEEN FLOOR(LEAST(fraddl,fraddr)/100)*100 AND " \
                "CEILING(GREATEST(toaddl,toaddr)/100)*100" % \
                (self.tables['edges'], ix_streetname, num)
            if not self.executeDict(Q): return None
        return self.getSegmentById(self.fetchRow()["ix"])


    def getSegmentByNodeIds(self, id_node_f, id_node_t):
        Q = "SELECT ix FROM %s WHERE " \
            "(id_node_f=%s AND id_node_t=%s) OR " \
            "(id_node_f=%s AND id_node_t=%s)" % \
            (self.tables['edges'], id_node_f, id_node_t, id_node_t, id_node_f)
        if not self.executeDict(Q): return None
        return self.getSegmentById(self.fetchRow()["ix"])


    # Utility Methods ---------------------------------------------------------

    def getRowsById(self, table, ixs, dict=True):
        """Fetch from table rows with row IDs. Return dict of {ixs=>row}."""
        result = {}
        Q = 'SELECT * FROM %s WHERE ix IN (%s)' % \
            (table, ','.join([str(i) for i in ixs]))
        if dict:
            self.executeDict(Q)
            for r in self.fetchAllDict(): result[r['ix']] = r
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
