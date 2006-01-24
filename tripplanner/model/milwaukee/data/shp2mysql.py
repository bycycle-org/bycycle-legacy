# Milwaukee shapefile import
import sys, os
from pysqlite2 import dbapi2 as sqlite
from byCycle.lib import gis, meter

dbf_fields = ('TLID', 'FNODE', 'TNODE',
              'FRADDL', 'TOADDL', 'FRADDR', 'TOADDR',
              'FEDIRP', 'FENAME', 'FETYPE', 'FEDIRS',
              'CITYL', 'CITYR', 'ZIPL', 'ZIPR',
              'CFCC', 'Bike_facil', 'GRADE', 'LANES', 'ADT', 'SPD', 'one_way') 

layer_fields = ('fnode', 'tnode',
                'addr_f', 'addr_t', 'streetname_id', 'city_l_id', 'city_r_id',
                'state_l_id', 'state_r_id', 'zipl', 'zipr', 'wkt_geometry')

attr_fields = ('one_way', 'cfcc', 'bike_facil', 'lanes', 'adt', 'spd')

# DB connection and cursor
con, cur = None, None
    


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
          '%s %s %s -nln %s'  % \
          (outsrs, outformat,
           ','.join(dbf_fields), 
           outdb, datasource, inlayer, outtable)
    print cmd
    exit_code = os.system(cmd)
    if exit_code:
        sys.exit()
    timer.stopTiming()

def fixRaw():
    ## Add missing columns
    Q = 'ALTER TABLE raw ADD COLUMN %s'
    cols = ('addr_f', 'addr_t', 'streetname_id', 'city_l_id', 'city_r_id',
            'state_l_id', 'state_r_id')
    for col in cols:
        execute(Q % col)
    ## Set TEXT NULLs to '' and all TEXT values to lower case
    Q0 = 'UPDATE raw SET %s="" WHERE %s IS NULL'
    Q1 = 'UPDATE raw SET %s=lower(%s)'
    cols = ('fedirp', 'fename', 'fetype', 'fedirs', 'cityl', 'cityr',
            'state_l_id', 'state_r_id', 'wkt_geometry',
            'cfcc', 'bike_facil')
    for col in cols:
        # TEXT NULL to ''
        execute(Q0 % (col, col))
        # TEXT to lower
        execute(Q1 % (col, col))
    con.commit()
    # Set INTEGER NULLs to 0
    Q = 'UPDATE raw SET %s=0 WHERE %s IS NULL'
    cols = ('fnode', 'tnode',
            'addr_f', 'addr_t', 'fraddl', 'toaddl', 'fraddr', 'toaddr',
            'streetname_id', 'city_l_id', 'city_r_id', 'zipl', 'zipr',
            'tlid', 'lanes', 'adt', 'spd', 'one_way')
    for col in cols:
        execute(Q % (col, col))
    con.commit()
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
        execute(Q)
    # Convert fraddl et al to integer type
    Q = 'SELECT rowid, fraddl, fraddr, toaddl, toaddr, tlid FROM raw'
    execute(Q)
    rows = cur.fetchall()
    Q = 'UPDATE raw ' \
        'SET fraddl=%s,fraddr=%s,toaddl=%s,toaddr=%s,tlid="%s" ' \
        'WHERE rowid=%s'
    for row in rows:
        execute(Q % (int(float(row[1])), int(float(row[2])),
                       int(float(row[3])), int(float(row[4])),
                       int(float(row[5])),
                       row[0]))
    # Fix broken geometry
    Q = 'SELECT rowid, wkt_geometry FROM raw ' \
        'WHERE wkt_geometry NOT LIKE "linestring (%)"'
    execute(Q)
    rows = cur.fetchall()
    for row in rows:
        id = row[0]
        geom = row[1]
        if 'empty' in geom:
            print 'Found empty street geometry: %s' % geom
            execute('UPDATE raw ' \
                      'SET wkt_geometry="linestring (0 0,1 1)"' \
                      'WHERE rowid=%s' % id)
        else:
            geom = geom.replace('multilinestring', '')
            geom = geom.replace('(', '')
            geom = geom.replace(')', '')
            geom = geom.strip()
            geom = 'linestring (%s)' % geom
            execute('UPDATE raw SET wkt_geometry="%s"' \
                      'WHERE rowid=%s' % (geom, id))                
    con.commit()

def unifyAddressRanges():
    Q = 'UPDATE raw ' \
        'SET addr_%s=(ROUND(%sadd%s / 10.0) * 10) ' \
        'WHERE %sadd%s != 0'
    for f in (('f', 'fr'), ('t', 'to')):
        for l in ('l', 'r'):
            execute(Q % (f[0], f[1], l, f[1], l))
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
        execute(Q)
    con.commit()

def transferStreetNames():
    """Transfer street names to their own table."""
    Q = 'INSERT INTO streetname (prefix, name, type, suffix) '\
        'SELECT DISTINCT fedirp, fename, fetype, fedirs FROM raw'
    execute(Q)
    con.commit()

def updateRawStreetNameIds():
    """Set the street name ID of each raw record."""
    # Get all the distinct street names
    Q = 'SELECT DISTINCT fedirp, fename, fetype, fedirs FROM raw'
    execute(Q)
    rows = cur.fetchall()
    # Index each street name ID by its street name
    # {(stname)=>streetname_id}
    stnames = {}
    Q = 'SELECT rowid, prefix, name, type, suffix FROM streetname'
    execute(Q)
    for row in cur.fetchall():
        stnames[(row[1],row[2],row[3],row[4])] = row[0]
    # Index raw row IDs by their street name ID {streetname_id=>[row IDs]}
    stid_rawids = {}
    Q  = 'SELECT rowid, fedirp, fename, fetype, fedirs FROM raw'
    execute(Q)
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
        execute(Q % (stid, tuple(ixs)))
        met.update(record_number)
        record_number+=1
    print  # newline after the progress meter
    con.commit()

def transferCityNames():
    """Transfer city names to their own table."""
    Q = 'INSERT INTO city (city) ' \
        'SELECT DISTINCT cityl FROM raw'
    execute(Q)
    Q = 'INSERT INTO city (city) ' \
        'SELECT DISTINCT cityr FROM raw WHERE cityr NOT IN ' \
        '(SELECT city FROM city)'
    execute(Q)
    con.commit()

def updateRawCityIds():
    """Set the city ID of each raw record."""
    for side in ('l', 'r'):
        Q0 = 'SELECT DISTINCT rowid, city FROM city'
        Q1 = 'UPDATE raw SET city_%s_id=%s WHERE city%s="%s"' % \
             (side, '%s', side, '%s')
        # Get all the distinct city names
        execute(Q0)
        rows = cur.fetchall()
        # Iterate over city rows and set city IDs of raw records
        for row in rows:
            execute(Q1 % (row[0], row[1]))
    con.commit()

def updateRawStateIds():
    """Set the state ID of each raw record."""
    Q = 'INSERT INTO state VALUES ("wi", "wisconsin")'
    execute(Q)
    Q = 'UPDATE raw SET state_l_id="wi", state_r_id="wi"'
    execute(Q)
    con.commit()

def createNodes():
    Q1 = 'SELECT rowid, fnode, tnode, wkt_geometry FROM raw'
    Q2 = 'UPDATE raw SET wkt_geometry="%s" WHERE rowid=%s'
    Q3 = 'INSERT INTO layer_node (id, wkt_geometry) VALUES (%s, "%s")'
    seen_node_ids = {}
    # Get node_ids and geometry from raw table
    execute(Q1)
    # Insert node IDs into layer_node, skipping the ones we've already seen
    for row in cur.fetchall():
        id = row[0]
        node_f_id, node_t_id = row[1], row[2]
        linestring = row[3]
        points = gis.importWktGeometry(linestring.lower())
        # Create a new linestring with only 6 decimal places in each number
        linestring = 'linestring (%s)' % ','.join(['%.6f %.6f' % (p.x, p.y) 
                                                   for p in points])
        execute(Q2 % (linestring, id))
        # Create and insert a WKT point for each end of the segment
        i = 0
        for node_id in (node_f_id, node_t_id):
            if node_id not in seen_node_ids:
                seen_node_ids[node_id] = 1
                p = points[i]
                execute(Q3 % (node_id, ('point (%.6f %.6f)'%(p.x, p.y))))
            i = -1
    con.commit()

def transferAttrs():
    ## Transfer core attributes to street table
    Q = 'INSERT INTO layer_street ' \
        'SELECT rowid, %s ' \
        'FROM raw' % \
        (','.join(layer_fields))
    execute(Q)
    ## Transfer extra attributes to attributes table (attrs)
    Q = 'INSERT INTO attr_street ' \
        'SELECT rowid, %s ' \
        'FROM raw' % \
        (','.join(attr_fields))
    execute(Q)
    con.commit()

def cleanUp():
    ## Clean up
    Qs = ('DROP TABLE raw', 'VACUUM')
    for Q in Qs: 
        execute(Q)
    cur.close()
    con.close()

def execute(Q):
    if cur is None:
        openDB()
    try:
        cur.execute(Q)
    except Exception, e:
        print 'Failed: %s\n\t%s' % (Q, e)
        sys.exit()

def openDB():
    ## Set up DB connection
    global con, cur
    con = sqlite.connect('db.db')
    cur = con.cursor()


if __name__ == '__main__':
    # This timer gets reused in the functions above
    timer = meter.Timer()    
    timer.startTiming('Transferring data into byCycle schema...')

    pairs = [('Converting shapefile to monolithic SQL table.',
              shpToRawSql),

             ('Creating byCycle schema tables.',
              os.system, ('sqlite3 db.db < ./schema.sql',)),

             ('Opening DB connection', openDB),
    
             ('Fixing raw table: Removing NULLs, adding columns, etc.',
              fixRaw),
             
             ('Unifying address ranges.',
              unifyAddressRanges),
             
             ('Transferring street names.',
              transferStreetNames),
             
             ('Updating street name IDs in raw table.',
              updateRawStreetNameIds),
             
             ('Updating city IDs in raw table.',
              updateRawCityIds),
             
             ('Transferring city names.',
              transferCityNames),
             
             ('Updating city IDs in raw table.',
              updateRawCityIds),
             
             ('Updating state IDs in raw table.',
              updateRawStateIds),
             
             ('Creating nodes.',
              createNodes),
             
             ('Transferring attributes.',
              transferAttrs),

             ('Cleaning up.',
             cleanUp),
             ]

    for p in pairs[-4:]:
        msg, func = p[0], p[1]
        try:
            args = p[2]
        except IndexError:
            args = ()
        timer.startTiming(msg)
        apply(func, args)
        timer.stopTiming()

    timer.stopTiming()
    print 'Done.'

