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
        # For ramdisk
        #self.matrix_path = '%stripplanner/model/data/%s_matrix.pyc' % \
        #                   (install_path, self.dmode)
        self.matrix_path = '%smatrix.pyc' % (self.data_path)
        
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
        Q = 'SELECT node_f_id, node_t_id, addr_f, addr_t, streetname_id, ' \
            'wkt_geometry ' \
            'FROM %s ' \
            'WHERE node_f_id IN (%s) OR node_t_id IN (%s)' % \
            (self.tables['edges'], id_str, id_str)
        self.executeDict(Q)
        rows = self.fetchAllDict()
        if rows:
            # Pre-fetch segments and index by both node_f_id and node_t_id
            seg_rows = {}
            streetname_ids = {}
            for row in rows:
                node_f_id, node_t_id = row['node_f_id'], row['node_t_id']
                if node_f_id in seg_rows: seg_rows[node_f_id].append(row)
                else: seg_rows[node_f_id] = [row]
                if node_t_id in seg_rows: seg_rows[node_t_id].append(row)
                else: seg_rows[node_t_id] = [row]
                streetname_ids[row['streetname_id']] = 1
                
            # Pre-fetch full street names
            streetnames = self.getRowsById(self.tables['streetnames'],
                                           streetname_ids.keys())
            streets = {}
            for streetname_id in streetnames:
                r = streetnames[streetname_id]
                st = address.Street(r['prefix'], r['name'],
                                    r['type'], r['suffix'])
                streets[streetname_id] = st
                
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
                node_f_id, node_t_id =  row['node_f_id'],  row['node_t_id']
                if id == node_f_id:
                    data['id'] = node_f_id
                    data['lon_lat'] = linestring[0]
                elif id == node_t_id:
                    data['id'] = node_t_id
                    data['lon_lat'] = linestring[-1]
                # Get all segments that have the intersection at one end
                S = seg_rows[id]
                # Get the cross streets
                cs = []
                seen_streetname_ids = {}
                for seg_row in S:
                    streetname_id = seg_row['streetname_id']
                    # Skip the segment if we've already seen a segment
                    # attached to this intersection that has the same
                    # street name (ID)
                    if streetname_id in seen_streetname_ids: continue
                    else: seen_streetname_ids[streetname_id] = 1
                    # Get segment street name
                    try: st = streets[streetname_id]
                    except KeyError:
                        st = address.Street(name='unknown')
                        st.number = -1
                    else: 
                        node_f_id = seg_row['node_f_id']
                        node_t_id = seg_row['node_t_id']
                        addr_f, addr_t = seg_row['addr_f'], seg_row['addr_t']
                        # Determine the street number at the intersection
                        if node_f_id == id:
                            num = addr_f
                        elif node_t_id == id:
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


    def getIntersectionClosestToSTIDandNum(self, streetname_id, num, lon_lat=None):
        """Get the intersection closest to the specified street address.

        @param streetname_id -- the id of the addresses's street name
        @param num -- the street number of the address
        @param lon_lat -- the lon/lat of the address (if known)
        @return -- the closest intersection and the intersection accross from
                   it on the segment containing address

        """
        # First get the distance of the closest intersection (by street number)
        Q = "SELECT node_f_id, node_t_id, " \
            "ABS(fraddl-%s) AS fl, ABS(fraddr-%s) AS fr, " \
            "ABS(toaddl-%s) AS tl, ABS(toaddr-%s) AS tr, " \
            "LEAST(ABS(fraddl-%s), ABS(fraddr-%s), " \
            "      ABS(toaddl-%s), ABS(toaddr-%s)) AS m " \
            "FROM %s WHERE streetname_id=%s ORDER BY m ASC LIMIT 1" % \
            (num, num, num, num, num, num, num, num,
             self.tables['edges'], streetname_id)

        if not self.executeDict(Q): return None, None
        row = self.fetchRow()

        m, fl, fr, tl, tr = row["m"], row["fl"], row["fr"], row["tl"], row["tr"]
        if m in (fl, fr):
            idc = row["node_f_id"]
            ida = row["node_t_id"]
        elif m in (tl, tr):
            idc = row["node_t_id"]
            ida = row["node_f_id"]

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
        streetname_ids, num = self.getStreetIdsForAddress(addr=addr)
        streetname_id, full_name = streetname_ids.popitem()
        i = self.getIntersectionClosestToSTIDandNum(streetname_id, num, lon_lat)
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

    def getSegmentsById(self, ids):
        if not ids: return []
        segments = []
        ids_str = ','.join([str(t) for t in ids])

        # Get segments with id in ids
        Q = 'SELECT * FROM %s WHERE id IN (%s)' % \
            (self.tables['edges'], ids_str)
        self.executeDict(Q)
        rows = self.fetchAllDict()

        if rows:
            # Index rows by id
            irows = {}
            for row in rows: irows[row['id']] = row

            # Add the extra attributes to the row
            Q = 'SELECT * FROM attr_street WHERE id IN (%s)' % ids_str
            self.executeDict(Q)
            arows = self.fetchAllDict()
            for i, arow in enumerate(arows):
                id = arow['id']
                irows[id].update(arow)
            del arows

            # Pre-fetch street names and cities
            streetname_ids, cityids = {}, {}
            for row in rows:
                streetname_ids[row['streetname_id']] = 1
                cityids[row['city_l_id']], cityids[row['city_r_id']] = 1, 1
            street_names = self.getRowsById(self.tables['streetnames'], 
                                            streetname_ids.keys())
            cities = self.getRowsById(self.tables['cities'], cityids.keys())

            # Get segments with the help of our pre-fetched data
            for id in ids:
                try:
                    row = irows[id]
                except KeyError:
                    segments.append(None)
                    continue
                # Get street name components, removing the id entry first
                street = street_names[row['streetname_id']]
                try: del street['id']
                except KeyError: pass
                row.update(street)
                row['street'] = address.Street(row['prefix'], row['name'],
                                               row['type'], row['suffix'])
                # Get city names for each side
                row['city_l'] = cities[row['city_l_id']]['city']
                row['city_r'] = cities[row['city_r_id']]['city']
                # Convert WKT linestring to list of points
                geom = row['wkt_geometry']
                row['linestring'] = gis.importWktGeometry(geom)
                # Append current segment to output list
                segments.append(segment.Segment(row))
        return segments

    
    def getSegmentById(self, id):
        """Get a segment with specified ID.

        @param id -- segment ID
        @return -- a segment object or None

        """
        return self.getSegmentsById([id])[0]


    def getSegmentByNumStreetId(self, num, streetname_id):
        Q = "SELECT id FROM %s " \
            "WHERE streetname_id=%s AND " \
            "%s BETWEEN LEAST(fraddl,fraddr) AND GREATEST(toaddl,toaddr)" % \
            (self.tables['edges'], streetname_id, num)
        if not self.executeDict(Q):
            Q = "SELECT id FROM %s " \
                "WHERE streetname_id=%s AND " \
                "%s BETWEEN FLOOR(LEAST(fraddl,fraddr)/100)*100 AND " \
                "CEILING(GREATEST(toaddl,toaddr)/100)*100" % \
                (self.tables['edges'], streetname_id, num)
            if not self.executeDict(Q): return None
        return self.getSegmentById(self.fetchRow()["id"])


    def getSegmentByNodeIds(self, node_f_id, node_t_id):
        Q = "SELECT id FROM %s WHERE " \
            "(node_f_id=%s AND node_t_id=%s) OR " \
            "(node_f_id=%s AND node_t_id=%s)" % \
            (self.tables['edges'], node_f_id, node_t_id, node_t_id, node_f_id)
        if not self.executeDict(Q): return None
        return self.getSegmentById(self.fetchRow()["id"])


    # Utility Methods ---------------------------------------------------------

    def getRowsById(self, table, ids, dict=True):
        """Fetch from table rows with row IDs. Return dict of {ids=>row}."""
        result = {}
        Q = 'SELECT * FROM %s WHERE id IN (%s)' % \
            (table, ','.join([str(i) for i in ids]))
        if dict:
            self.executeDict(Q)
            for r in self.fetchAllDict(): result[r['id']] = r
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
