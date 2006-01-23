# Milwaukee shapefile import
import sys, os
from pysqlite2 import dbapi2 as sqlite
from byCycle.lib import meter

dbf_fields = ('TLID', 'FNODE', 'TNODE',
              'FRADDL', 'TOADDL', 'FRADDR', 'TOADDR',
              'FEDIRP', 'FENAME', 'FETYPE', 'FEDIRS',
              'CITYL', 'CITYR', 'ZIPL', 'ZIPR',
              'CFCC', 'Bike_facil', 'GRADE', 'LANES', 'ADT', 'SPD', 'one_way')

layre_fields = ('wkt_geometry', 'fnode', 'tnode',
                'addr_f', 'addr_t', 'streetname_id', 'city_l_id', 'city_r_id',
                'state_l_id', 'state_r_id', 'zipl', 'zipr')

attr_fields = ('tlid', 'one_way', 'cfcc', 'bike_facil', 'grade', 'lanes',
               'adt', 'spd')


def shpToRawSql():
    timer.startTiming('Converting shapefile to monolithic SQL table.')
    try:
        os.unlink('db.db')
        os.unlink('db.db-journal')
    except OSError, e:
        print e
    datasource = 'route_roads84_without_bike_trails'
    inlayer = 'route_roads84work'
    outdb = 'db.db'
    outtable = 'raw'
    outsrs = '' #'-t_srs WGS84'
    outformat = 'SQLite'
    ds = os.getcwd()
    cmd = 'ogr2ogr %s -f "%s" ' \
          '-select "%s" ' \
          '%s %s %s -nln %s'  % (outsrs, outformat, ','.join(dbf_fields[0:15]), 
                                 outdb, datasource, inlayer, outtable)
    print cmd
    exit_code = os.system(cmd)
    if exit_code:
        sys.exit()
    timer.stopTiming()


def sqlToSql():
    def __fixRaw():
        ## Add missing columns
        Q = 'ALTER TABLE raw ADD COLUMN %s'
        cols = ('addr_f', 'addr_t', 'streetname_id', 'city_l_id', 'city_r_id',
                'state_l_id', 'state_r_id')
        for col in cols:
            __execute(Q % col)
        ## Set TEXT NULLs to '' and all TEXT values to lower case
        Q0 = 'UPDATE raw SET %s="" WHERE %s IS NULL'
        Q1 = 'UPDATE raw SET %s=lower(%s)'
        cols = ('fedirp', 'fename', 'fetype', 'fedirs', 'cityl', 'cityr',
                'state_l_id', 'state_r_id', 'wkt_geometry',
                'cfcc', 'bike_facil', 'grade')
        for col in cols:
            # TEXT NULL to ''
            ###__execute(Q0 % (col, col))
            # TEXT to lower
            __execute(Q1 % (col, col))
        con.commit()
        # Set INTEGER NULLs to 0
        Q = 'UPDATE raw SET %s=0 WHERE %s IS NULL'
        cols = ('fnode', 'tnode',
                'addr_f', 'addr_t', 'fraddl', 'toaddl', 'fraddr', 'toaddr',
                'streetname_id', 'city_l_id', 'city_r_id', 'zipl', 'zipr',
                'tlid', 'lanes', 'adt', 'spd', 'one_way')
        ###for col in cols:
        ###    __execute(Q % (col, col))
        ###con.commit()
        # Abbreviate bike modes
        Qs = ('UPDATE raw SET bike_facil="t" ' \
              'WHERE bike_facil="bike trail"',
              'UPDATE raw SET bike_facil="r" ' \
              'WHERE bike_facil="bike route"',
              'UPDATE raw SET bike_facil="l" ' \
              'WHERE bike_facil="bike lane"',
              'UPDATE raw SET bike_facil="p" ' \
              'WHERE bike_facil="preferred street"',
              'UPDATE raw SET cfcc="a71" ' \
              'WHERE bike_facil="bt"',
              )
        for Q in Qs:
            __execute(Q)
        # Convert fraddl et al to integer type
        Q = 'SELECT rowid, fraddl, fraddr, toaddl, toaddr, tlid FROM raw'
        __execute(Q)
        rows = cur.fetchall()
        Q = 'UPDATE raw ' \
            'SET fraddl=%s,fraddr=%s,toaddl=%s,toaddr=%s,tlid="%s" ' \
            'WHERE rowid=%s'
        for row in rows:
            __execute(Q % (int(float(row[1])), int(float(row[2])),
                           int(float(row[3])), int(float(row[4])),
                           int(float(row[5])),
                           row[0]))
        # Fix broken geometry
        Q = 'SELECT rowid, wkt_geometry FROM raw ' \
            'WHERE wkt_geometry NOT LIKE "linestring (%)"'
        __execute(Q)
        rows = cur.fetchall()
        for row in rows:
            id = row[0]
            geom = row[1]
            if 'empty' in geom:
                print 'Found empty street geometry: %s' % geom
                __execute('UPDATE raw SET wkt_geometry="linestring (0 0,1 1)"' \
                          'WHERE rowid=%s' % id)
            else:
                geom = geom.replace('multilinestring', '')
                geom = geom.replace('(', '')
                geom = geom.replace(')', '')
                geom = geom.strip()
                geom = 'linestring (%s)' % geom
                __execute('UPDATE raw SET wkt_geometry="%s"' \
                          'WHERE rowid=%s' % (geom, id))                
        con.commit()

    def __unifyAddressRanges():
        Q = 'UPDATE raw ' \
            'SET addr_%s=(ROUND(%sadd%s / 10.0) * 10) ' \
            'WHERE %sadd%s != 0'
        for f in (('f', 'fr'), ('t', 'to')):
            for l in ('l', 'r'):
                __execute(Q % (f[0], f[1], l, f[1], l))
        # Encode from address
        #     Ends in 0, left side of segment even
        #     Ends in 1, left side of segment odd
        Qs = ('UPDATE raw SET addr_f = (addr_f + (fraddl % 2)) ' \
              'WHERE fraddl != 0 AND (addr_f % 2 = 0)',
              
              'UPDATE raw SET addr_f = (addr_f + (1 - (fraddr % 2))) ' \
              'WHERE fraddr != 0 AND (addr_f % 2 = 0)',
              
              'UPDATE raw SET addr_f = (addr_f + (toaddl % 2)) ' \
              'WHERE toaddl != 0 AND (addr_f % 2 = 0)',

              'UPDATE raw SET addr_f = (addr_f + (1 - (toaddr % 2))) ' \
              'WHERE toaddr != 0 AND (addr_f % 2 = 0)')
        for Q in Qs:
            __execute(Q)
        con.commit()
        
    def __transferStreetNames():
        """Transfer street names to their own table."""
        Q = 'INSERT INTO streetname (prefix, name, type, suffix) '\
            'SELECT DISTINCT fedirp, fename, fetype, fedirs FROM raw'
        __execute(Q)
        con.commit()

    def __updateRawStreetNameIds():
        """Set the street name ID of each raw record."""
        # Get all the distinct street names
        Q = 'SELECT DISTINCT fedirp, fename, fetype, fedirs FROM raw'
        __execute(Q)
        rows = cur.fetchall()
        # Index each street name ID by its street name
        # {(stname)=>streetname_id}
        stnames = {}
        Q = 'SELECT rowid, prefix, name, type, suffix FROM streetname'
        __execute(Q)
        for row in cur.fetchall():
            stnames[(row[1],row[2],row[3],row[4])] = row[0]
        # Index raw row IDs by their street name ID {streetname_id=>[row IDs]}
        stid_rawids = {}
        Q  = 'SELECT rowid, fedirp, fename, fetype, fedirs FROM raw'
        __execute(Q)
        for row in cur.fetchall():
            stid = stnames[(row[1],row[2],row[3],row[4])]
            if stid in stid_rawids: stid_rawids[stid].append(row[0])
            else: stid_rawids[stid] = [row[0]]
        # Iterate over street name IDs and set street name IDs of raw records
        Q = 'UPDATE raw SET streetname_id=%s WHERE rowid IN %s'
        met = meter.Meter()
        met.setNumberOfItems(len(stid_rawids))
        met.startTimer()
        record_number = 1
        for stid in stid_rawids:
            ixs = stid_rawids[stid]
            __execute(Q % (stid, tuple(ixs)))
            met.update(record_number)
            record_number+=1
        print  # newline after the progress meter
        con.commit()

    def __transferCityNames():
        """Transfer city names to their own table."""
        Q = 'INSERT INTO city (city) ' \
            'SELECT DISTINCT cityl FROM raw'
        __execute(Q)
        Q = 'INSERT INTO city (city) ' \
            'SELECT DISTINCT cityr FROM raw WHERE cityr NOT IN ' \
            '(SELECT city FROM city)'
        __execute(Q)
        con.commit()
        
    def __updateRawCityIds():
        """Set the city ID of each raw record."""
        for side in ('l', 'r'):
            Q0 = 'SELECT DISTINCT rowid, city FROM city'
            Q1 = 'UPDATE raw SET city_%s_id=%s WHERE city%s="%s"' % \
                 (side, '%s', side, '%s')
            # Get all the distinct city names
            __execute(Q0)
            rows = cur.fetchall()
            # Iterate over city rows and set city IDs of raw records
            met = meter.Meter()
            met.setNumberOfItems(len(rows))
            met.startTimer()
            record_number = 1
            for row in rows:
                __execute(Q1 % (row[0], row[1]))
                met.update(record_number)
                record_number+=1
            #print  # newline after the progress meter
        con.commit()

    def __updateRawStateIds():
        """Set the state ID of each raw record."""
        Q = 'INSERT INTO state VALUES (NULL, "wi", "wisconsin")'
        __execute(Q)
        Q = 'UPDATE raw SET state_l_id="wi", state_r_id="wi"'
        __execute(Q)
        con.commit()

    def __createNodes():
        Q1 = 'SELECT fnode, tnode, wkt_geometry FROM raw'
        Q2 = 'INSERT INTO layer_node (id, wkt_geometry) VALUES (%s, "%s")'
        seen_node_ids = {}
        # Get node_ids and geometry from raw table
        __execute(Q1)
        # Insert node IDs into layer_node, skipping the ones we've already seen
        for row in cur.fetchall():
            ix = 0
            node_f_id, node_t_id = row[0], row[1]
            linestring, points = row[2], None
            for node_id in (node_f_id, node_t_id):
                if node_id not in seen_node_ids:
                    seen_node_ids[node_id] = 1
                    if not points:
                        # '(x y,x y)'
                        points = linestring.split(' ', 1)[1].strip() 
                        # ['x y', 'x y']
                        points = [w.strip()
                                  for w
                                  in points[1:-1].strip().split(',')]
                    __execute(Q2 % (node_id, ('point (%s)' % points[ix])))
                ix = -1
        con.commit()

    def __transferAttrs():
        ## Transfer core attributes to street table
        Q = 'INSERT INTO layer_street ' \
            'SELECT rowid, %s ' \
            'FROM raw' % \
            (','.join(layer_fields))
        __execute(Q)
        ## Transfer extra attributes to attributes table (attrs)
        Q = 'INSERT INTO attr_street ' \
            'SELECT rowid, %s ' \
            'FROM raw' % \
            (','.join(attr_fields))
        __execute(Q)
        con.commit()

    def __cleanUp():
        Qs = ('DROP TABLE raw', 'VACUUM')
        for Q in Qs: 
            __execute(Q)

    def __execute(Q):
        try:
            cur.execute(Q)
        except Exception, e:
            print 'Failed: %s\n\t%s' % (Q, e)
            sys.exit()
        
    ## Set up DB connection
    con = sqlite.connect('db.db')
    cur = con.cursor()
    
    ## Do work
    timer.startTiming('Transferring data into byCycle schema...')

    pairs = [('Creating byCycle schema tables.',
              os.system, ('sqlite3 db.db < ./schema.sql',)),
    
             ('Fixing raw table: Removing NULLs, adding columns, etc.',
              __fixRaw),
             
             ('Unifying address ranges.',
              __unifyAddressRanges),
             
             ('Transferring street names.',
              __transferStreetNames),
             
             ('Updating street name IDs in raw table.',
              __updateRawStreetNameIds),
             
             ('Updating city IDs in raw table.',
              __updateRawCityIds),
             
             ('Transferring city names.',
              __transferCityNames),
             
             ('Updating city IDs in raw table.',
              __updateRawCityIds),
             
             ('Updating state IDs in raw table.',
              __updateRawStateIds),
             
             ('Creating nodes.',
              __createNodes),
             
             ('Transferring attributes.',
              __transferAttrs),

             ('Cleaning up.',
             __cleanUp),
             ]

    for p in pairs:
        msg, func = p[0], p[1]
        try: args = p[2]
        except IndexError: args = ()
        timer.startTiming(msg)
        apply(func, args)
        timer.stopTiming()

    cur.close()
    con.close()
    timer.stopTiming()


def test():
    pass

    
if __name__ == '__main__':
    test = 0
    
    main_timer = meter.Timer()
    main_timer.startTiming('Here goes...')

    # This timer gets reused in the functions above
    timer = meter.Timer()    

    if test:
        test()
    else:
        shpToRawSql()
        sqlToSql()

    main_timer.stopTiming()
    print 'Done.'

