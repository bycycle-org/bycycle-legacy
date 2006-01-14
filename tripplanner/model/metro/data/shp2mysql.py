import sys, os
from pysqlite2 import dbapi2 as sqlite
from byCycle.lib import meter


def shpToRawSql():
    timer.startTiming('Converting shapefile to monolithic SQL table.')
    try:
        os.unlink('db.db')
        os.unlink('db.db-journal')
    except OSError, e:
        print e
    inlayer = 'route_roads84'
    outdb = 'db.db'
    outtable = 'raw'
    outsrs = '' #'-t_srs WGS84'
    outformat = 'SQLite'
    ds = os.getcwd()
    cmd = 'ogr2ogr %s -f "%s" ' \
          '-select "TLID,ID_NODE_F,ID_NODE_T,PREFIX,NAME,TYPE,SUFFIX,CFCC,' \
          'ADDR_FL,ADDR_TL,ADDR_FR,ADDR_TR,CITY_L,CITY_R,ZIP_L,ZIP_R,' \
          'BIKEMODE,GRADE,LANES,ADT,SPD,ONEWAY" ' \
          '%s . %s -nln %s'  % (outsrs, outformat, outdb, inlayer, outtable)
    print cmd
    exit_code = os.system(cmd)
    if exit_code:
        sys.exit()
    timer.stopTiming()


def sqlToSql():
    def __fixRaw():
        ## Add missing columns
        Q = 'ALTER TABLE raw ADD COLUMN %s'
        cols = ('addr_f', 'addr_t', 'ix_streetname', 'ix_city_l', 'ix_city_r',
                'id_state_l', 'id_state_r')
        for col in cols:
            __execute(Q % col)
        ## Set TEXT NULLs to '' and all TEXT values to lower case
        Q0 = 'UPDATE raw SET %s="" WHERE %s IS NULL'
        Q1 = 'UPDATE raw SET %s=lower(%s)'
        cols = ('prefix', 'name', 'type', 'suffix', 'city_l', 'city_r',
                'id_state_l', 'id_state_r', 'wkt_geometry',
                'cfcc', 'bikemode', 'grade')
        for col in cols:
            # TEXT NULL to ''
            __execute(Q0 % (col, col))
            # TEXT to lower
            __execute(Q1 % (col, col))
        con.commit()
        # Set INTEGER NULLs to 0
        Q = 'UPDATE raw SET %s=0 WHERE %s IS NULL'
        cols = ('id_node_f', 'id_node_t',
                'addr_f', 'addr_t', 'addr_fl', 'addr_tl', 'addr_fr', 'addr_tr',
                'ix_streetname', 'ix_city_l', 'ix_city_r', 'zip_l', 'zip_r',
                'tlid', 'lanes', 'adt', 'spd', 'oneway')
        for col in cols:
            __execute(Q % (col, col))
        con.commit()

    def __unifyAddressRanges():
        Q = 'UPDATE raw ' \
            'SET addr_%s=(ROUND(addr_%s%s / 10.0) * 10) ' \
            'WHERE addr_%s%s != 0'
        for f in ('f', 't'):
            for l in ('l', 'r'):
                __execute(Q % (f, f, l, f, l))
        Qs = ('UPDATE raw SET addr_f = (addr_f + (addr_fl % 2)) ' \
              'WHERE addr_fl != 0 AND (addr_f % 2 = 0)',
              'UPDATE raw SET addr_f = (addr_f + (1 - (addr_fr % 2))) ' \
              'WHERE addr_fr != 0 AND (addr_f % 2 = 0)',
              'UPDATE raw SET addr_f = (addr_f + (addr_tl % 2)) ' \
              'WHERE addr_tl != 0 AND (addr_f % 2 = 0)',
              'UPDATE raw SET addr_f = (addr_f + (1 - (addr_tr % 2))) ' \
              'WHERE addr_tr != 0 AND (addr_f % 2 = 0)')
        for Q in Qs:
            __execute(Q)
        con.commit()
        
    def __transferStreetNames():
        """Transfer street names to their own table."""
        Q = 'INSERT INTO streetname (prefix, name, type, suffix) '\
            'SELECT DISTINCT prefix, name, type, suffix FROM raw'
        __execute(Q)
        con.commit()

    def __updateRawStreetNameIds():
        """Set the street name ID of each raw record."""
        # Get all the distinct street names NEW
        Q = 'SELECT DISTINCT prefix, name, type, suffix FROM raw'
        __execute(Q)
        rows = cur.fetchall()
        # Index each street name ID by its street name
        # {(stname)=>ix_streetname}
        stnames = {}
        Q = 'SELECT ix, prefix, name, type, suffix FROM streetname'
        __execute(Q)
        for row in cur.fetchall():
            stnames[(row[1],row[2],row[3],row[4])] = row[0]
        # Index raw row IDs by their street name ID {ix_streetname=>[row IDs]}
        stid_rawids = {}
        Q  = 'SELECT rowid, prefix, name, type, suffix FROM raw'
        __execute(Q)
        for row in cur.fetchall():
            stid = stnames[(row[1],row[2],row[3],row[4])]
            if stid in stid_rawids: stid_rawids[stid].append(row[0])
            else: stid_rawids[stid] = [row[0]]
        # Iterate over street name IDs and set street name IDs of raw records
        Q = 'UPDATE raw SET ix_streetname=%s WHERE rowid IN %s'
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
            'SELECT DISTINCT city_l FROM raw'
        __execute(Q)
        Q = 'INSERT INTO city (city) ' \
            'SELECT DISTINCT city_r FROM raw WHERE city_r NOT IN ' \
            '(SELECT city FROM city)'
        __execute(Q)
        con.commit()
        
    def __updateRawCityIds():
        """Set the city ID of each raw record."""
        for side in ('l', 'r'):
            Q0 = 'SELECT DISTINCT ix, city FROM city'
            Q1 = 'UPDATE raw SET ix_city_%s=%s WHERE city_%s="%s"' % \
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
            print  # newline after the progress meter
        con.commit()

    def __updateRawStateIds():
        """Set the state ID of each raw record."""
        Q = 'INSERT INTO state VALUES (NULL, "wi", "wisconsin")'
        __execute(Q)
        Q = 'UPDATE raw SET id_state_l="wi", id_state_r="wi"'
        __execute(Q)
        con.commit()

    def __createNodes():
        Q1 = 'SELECT id_node_f, id_node_t, wkt_geometry FROM raw'
        Q2 = 'INSERT INTO layer_node (id, wkt_geometry) VALUES (%s, "%s")'
        seen_id_nodes = {}
        # Get id_nodes and geometry from raw table
        __execute(Q1)
        # Insert node IDs into layer_node, skipping the ones we've already seen
        for row in cur.fetchall():
            ix = 0
            id_node_f, id_node_t = row[0], row[1]
            linestring, points = row[2], None
            for id_node in (id_node_f, id_node_t):
                if id_node not in seen_id_nodes:
                    seen_id_nodes[id_node] = 1
                    if not points:
                        points = linestring.split(' ', 1)[1][1:-1].split(',')
                    __execute(Q2 % (id_node, ('POINT (%s)' % points[ix])))
                ix = -1
        con.commit()

    def __transferAttrs():
        ## Transfer core attributes to street table
        Q = 'INSERT INTO layer_street ' \
            'SELECT rowid, wkt_geometry, id_node_f, id_node_t, ' \
            'addr_f, addr_t, ix_streetname, ix_city_l, ix_city_r, ' \
            'id_state_l, id_state_r, zip_l, zip_r ' \
            'FROM raw'
        __execute(Q)
        ## Transfer extra attributes to attributes table (attrs)
        # Abbreviate bike modes first
        Qs = ('UPDATE attr_street SET bikemode="bt" ' \
              'WHERE bikemode="bike trail"',
              'UPDATE attr_street SET bikemode="br" ' \
              'WHERE bikemode="bike route"',
              'UPDATE attr_street SET bikemode="bl" ' \
              'WHERE bikemode="bike lane"',
              'UPDATE attr_street SET bikemode="ps" ' \
              'WHERE bikemode="preferred street"')
        for Q in Qs:
            __execute(Q)
        Q = 'INSERT INTO attr_street ' \
            'SELECT NULL,tlid,oneway,cfcc,bikemode,grade,lanes,adt,spd ' \
            'FROM raw'
        __execute(Q)
        con.commit()

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
             ]

    for p in pairs:
        msg, func = p[0], p[1]
        try: args = p[2]
        except IndexError: args = ()
        timer.startTiming(msg)
        apply(func, args)
        timer.stopTiming()

    ## Clean up
    Q = 'DROP TABLE raw'
    __execute(Q)
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

