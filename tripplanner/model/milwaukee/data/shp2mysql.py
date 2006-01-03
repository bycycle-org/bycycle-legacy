import sys
sys.path.append('../../..')

import os, marshal
from pysqlite2 import dbapi2 as sqlite
import meter


def shpToRawSql():
    timer.startTiming('Converting shapefile to monolithic SQL table.')
    try:
        os.unlink('db.db')
        os.unlink('db.db-journal')
    except OSError, e:
        print e
    import ogr
    inlayer = 'route_roads'
    outdb = 'db.db'
    outtable = 'raw'
    outsrs = 'WGS84'
    outformat = 'SQLite'
    ds = os.getcwd()
    cmd = 'ogr2ogr -t_srs "%s" -f "%s" ' \
          '-select "TLID,FNODE,TNODE,PREFIX,NAME,TYPE,SUFFIX,CFCC,' \
          'FRADDL,TOADDL,FRADDR,TOADDR,ZIPL,ZIPR,' \
          'BIKEMODE,GRADE,LANES,ADT,SPD,FEET,ONE_WAY" ' \
          '%s . %s -nln %s'  % (outsrs, outformat, outdb, inlayer, outtable)
    print cmd
    os.system(cmd)        
    timer.stopTiming()


def sqlToSql():
    def __fixRaw():
        ## Add missing columns
        Q = 'ALTER TABLE raw ADD COLUMN %s'
        cols = ('cityidl', 'cityidr', 'statecodel', 'statecoder', 'stnameid')
        for col in cols:
            try: cur.execute(Q % col)
            except Exception, e: print 'Failed: %s' % (Q % col)
        ## Set NULL values to appropriate zero value for column type
        ## Also, set TEXT fields to lower case
        Q = 'UPDATE raw SET %s="" WHERE %s IS NULL'
        Q1 = 'UPDATE raw SET %s=lower(%s)'
        cols = ('prefix', 'name', 'type', 'suffix', 'cityl', 'cityr',
                'statecodel', 'statecoder', 'wkt_geometry',
                'cfcc', 'bikemode', 'grade')
        for col in cols:
            try: cur.execute(Q % (col, col))
            except Exception, e: print 'Failed: %s' % (Q % (col, col))
            try: cur.execute(Q1 % (col, col))
            except Exception, e: print 'Failed: %s' % (Q % (col, col))
        con.commit()
        Q = 'UPDATE raw SET %s=0 WHERE %s IS NULL'
        cols = ('fnode', 'tnode', 'fraddl', 'toaddl', 'fraddr', 'toaddr',
                'stnameid', 'cityidl', 'cityidr', 'zipl', 'zipr',
                'tlid', 'lanes', 'adt', 'spd', 'feet', 'one_way')
        for col in cols:
            try: cur.execute(Q % (col, col))
            except Exception, e: print 'Failed: %s' % (Q % (col, col))
        con.commit()
        
    def __transferStreetNames():
        ## Transfer street names to their own table...
        # Convert NULLs to ''
        Q0 = 'UPDATE raw SET %s="" WHERE %s IS NULL'
        cols = ('prefix', 'name', 'type', 'suffix')
        for col in cols:
            try: cur.execute(Q0 % (col, col))
            except Exception, e: print Q0 % (col, col)
        # Do the actual insert
        Q = 'INSERT INTO streetnames (prefix, name, type, suffix) '\
            'SELECT DISTINCT prefix, name, type, suffix FROM raw'
        cur.execute(Q)
        con.commit()

    def __UpdateRawStreetNameIds():
        ## ...then set the street name ID of each record
        # Get all the distinct street names NEW
        Q = 'SELECT DISTINCT prefix, name, type, suffix FROM raw'
        cur.execute(Q)
        rows = cur.fetchall()
        # Index each street name ID by its street name {(stname)=>stnameid}
        stnames = {}
        Q = 'SELECT rowid, prefix, name, type, suffix FROM streetnames'
        cur.execute(Q)
        for row in cur.fetchall():
            stnames[(row[1],row[2],row[3],row[4])] = row[0]
        # Index raw row IDs by their street name ID {stnameid=>[row IDs]}
        stid_rawids = {}
        Q  = 'SELECT rowid, prefix, name, type, suffix FROM raw'
        cur.execute(Q )
        for row in cur.fetchall():
            stid = stnames[(row[1],row[2],row[3],row[4])]
            if stid in stid_rawids: stid_rawids[stid].append(row[0])
            else: stid_rawids[stid] = [row[0]]
        # Iterate over street name IDs and set street name IDs of raw records
        Q = 'UPDATE raw SET stnameid=%s WHERE rowid IN %s'
        met = meter.Meter()
        met.setNumberOfItems(len(stid_rawids))
        met.startTimer()
        record_number = 1
        for stid in stid_rawids:
            rowids = stid_rawids[stid]
            cur.execute(Q % (stid, tuple(rowids)))
            met.update(record_number)
            record_number+=1
        print  # newline after the progress meter
        con.commit()

    def __transferCityNames():
        ##    ## Transfer city names to their own table...
        ##    # Convert NULLs to ''
        ##    Q0 = 'UPDATE raw SET %s="" WHERE %s IS NULL'
        ##    cols = ('cityl', 'cityr')
        ##    for col in cols:
        ##        try: cur.execute(Q0 % (col, col))
        ##        except Exception, e: print Q0 % (col, col)
        ##    # Do the actual insert
        ##    cities = {}

        ##    Q = 'INSERT INTO cities (city) SELECT DISTINCT %s FROM raw'
        ##    cur.execute(Q)
        ##    con.commit()
        ##    timer.stopTiming()

        ##    ## ...then set the city IDs of each record
        ##    timer.startTiming('Updating city IDs.')
        ##    Q0 = 'SELECT DISTINCT cityl FROM raw'
        ##    Q1 = 'SELECT rowid FROM cities WHERE city="%s"'
        ##    Q2 = 'UPDATE raw SET cityidl=%s WHERE cityl="%s"'

        ##    # Get all the distinct city names
        ##    cur.execute(Q0)
        ##    rows = cur.fetchall()

        ##    # Iterate over city names and set city IDs of raw records
        ##    met = meter.Meter()
        ##    met.setNumberOfItems(len(rows))
        ##    met.startTimer()
        ##    record_number = 1
        ##    for row in rows:
        ##        # Get city ID for current city
        ##        cur.execute(Q1 % row)
        ##        stnameid = cur.fetchone()[0]
        ##        # Set the city IDs of all raw rows having current city name
        ##        cur.execute(Q2 % (stnameid, rowids))
        ##        met.update(record_number)
        ##        record_number+=1
        ##    print  # newline after the progress meter
        ##    con.commit()
        pass
            
    def __creatIntersections():
        ## Create intersections
        Q1 = 'SELECT fnode, tnode, wkt_geometry FROM raw'
        Q2 = 'INSERT INTO intersections (nid, wkt_geometry) VALUES (%s, "%s")'
        seen_nids = {}
        # Get nids and geometry from raw table
        cur.execute(Q1)
        # Insert nids into intersections, skipping the nids we've already seen
        for row in cur.fetchall():
            idx = 0
            fnode, tnode = row[0], row[1]
            linestring, points = row[2], None
            for nid in (fnode, tnode):
                if nid not in seen_nids:
                    seen_nids[nid] = 1
                    if not points:
                        points = linestring.split(' ', 1)[1][1:-1].split(',')
                    cur.execute(Q2 % (nid, ('POINT (%s)' % points[idx])))
                idx = -1
        con.commit()

    def __transferAttrs():
        ## Transfer core attributes to streets table
        Q = 'INSERT INTO streets ' \
            'SELECT NULL,fnode,tnode,fraddl,toaddl,fraddr,toaddr,stnameid,' \
            'cityidl,cityidr,statecodel,statecoder,zipl,zipr,wkt_geometry ' \
            'FROM raw'
        cur.execute(Q)
        ## Transfer extra attributes to attributes table (attrs)
        Q = 'INSERT INTO attrs ' \
            'SELECT NULL,tlid,cfcc,bikemode,grade,lanes,adt,spd,feet,one_way' \
            ' FROM raw'
        cur.execute(Q)
        con.commit()

    ## Set up DB connection
    con = sqlite.connect('db.db')
    cur = con.cursor()
    ## Do work
    timer.startTiming('Transferring raw table data into byCycle schema.')

    timer.startTiming('Creating byCycle schema tables.')
    os.system('sqlite3 db.db < ../../schema.sql')
    timer.stopTiming()
    
    timer.startTiming('Fixing raw table.')
    __fixRaw()
    timer.stopTiming()

    #timer.startTiming('Transferring city names.')
    #__transferCityNames
    #timer.stopTiming()

    #timer.startTiming('Updating city IDs in raw table.')
    #__UpdateRawCityIds()
    #timer.stopTiming()

    timer.startTiming('Transferring street names.')
    __transferStreetNames()
    timer.stopTiming()

    timer.startTiming('Updating street name IDs in raw table.')
    __UpdateRawStreetNameIds()
    timer.stopTiming()

    timer.startTiming('Creating intersections.')
    __creatIntersections()
    timer.stopTiming()

    timer.startTiming('Transferring attributes.')
    __transferAttrs()
    timer.stopTiming()

    ## Clean up
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

