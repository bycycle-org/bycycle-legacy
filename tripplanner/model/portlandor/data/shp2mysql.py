import sys, os
import MySQLdb as db
from byCycle.lib import gis, meter


dbf_fields = ('LOCALID', 'FNODE', 'TNODE',
              'LEFTADD1', 'LEFTADD2', 'RGTADD1', 'RGTADD2',
              'FDPRE', 'FNAME', 'FTYPE', 'FDSUF',
              'LCITY', 'RCITY', 'ZIPCOLEF', 'ZIPCORGT',
              'ONE_WAY', 'TYPE', 'BIKEMODE', 'UP_FRAC', 'ABS_SLP', 'CPD', 'SSCODE')

layer_fields = ('fnode', 'tnode',
                'addr_f', 'addr_t', 'streetname_id', 'city_l_id', 'city_r_id',
                'state_l_id', 'state_r_id', 'zipcolef', 'zipcorgt',
                'wkt_geometry')

attr_fields = ('localid', 'one_way', 'type', 'bikemode', 'up_frac', 'abs_slp', 'cpd', 'sscode')


def shpToRawSql():
    try:
        os.unlink('db.db')
        os.unlink('db.db-journal')
    except OSError, e:
        print e
    datasource = r'E:\GIS\_tp\str04\prj'
    inlayer = 'str_prj04aug'
    outdb = 'db.db'
    outtable = 'raw'
    outsrs = ''#'-t_srs WGS84'
    outformat = 'SQLite'
    ds = os.getcwd()
    cmd = r'C:\Progra~1\FWTools1.0.0a7\bin\ogr2ogr %s -f "%s" -select "%s" %s %s %s -nln %s' % \
          (outsrs, outformat,
           ','.join(dbf_fields), 
           outdb, datasource, inlayer, outtable)
    print cmd
    exit_code = os.system(cmd)
    if exit_code:
        sys.exit()

def fixRaw():
    ## Add missing columns
    Q = 'ALTER TABLE raw ADD COLUMN %s'
    cols = ('addr_f', 'addr_t', 'streetname_id', 'city_l_id', 'city_r_id',
            'state_l_id', 'state_r_id', 'code')
    for col in cols:
        execute(Q % col)
    con.commit()
    ## Set TEXT NULLs to '' and all TEXT values to lower case
    Q0 = 'UPDATE raw SET %s="" WHERE %s IS NULL'
    Q1 = 'UPDATE raw SET %s=lower(%s)'
    cols = ('fdpre', 'fname', 'ftype', 'fdsuf', 'lcity', 'rcity',
            'state_l_id', 'state_r_id', 'wkt_geometry',
            'one_way', 'bikemode')
    for col in cols:
        # TEXT NULL to ''
        execute(Q0 % (col, col))
        # TEXT to lower
        execute(Q1 % (col, col))
    con.commit()
    # Set INTEGER and FLOAT NULLs to 0
    Q = 'UPDATE raw SET %s=0 WHERE %s IS NULL'
    cols = ('fnode', 'tnode',
            'addr_f', 'addr_t',
            'leftadd1', 'leftadd2', 'rgtadd1', 'rgtadd2',
            'streetname_id', 'city_l_id', 'city_r_id',
            'zipcolef', 'zipcorgt',
            'up_frac', 'abs_slp')
    for col in cols:
        execute(Q % (col, col))
    con.commit()
    # Abbreviate bike modes
    Qs = ('UPDATE raw SET bikemode="t" ' \
          'WHERE bikemode="mu"',

          'UPDATE raw SET bikemode="p" ' \
          'WHERE bikemode="mm"',

          'UPDATE raw SET bikemode="b" ' \
          'WHERE bikemode="bl"',

          'UPDATE raw SET bikemode="l" ' \
          'WHERE bikemode="lt"',

          'UPDATE raw SET bikemode="m" ' \
          'WHERE bikemode="mt"',

          'UPDATE raw SET bikemode="h" ' \
          'WHERE bikemode="ht"',

          'UPDATE raw SET bikemode="c" ' \
          'WHERE bikemode="ca"',

          'UPDATE raw SET bikemode="x" ' \
          'WHERE bikemode="pm"',

          'UPDATE raw SET bikemode="x" ' \
          'WHERE bikemode="up"',

          'UPDATE raw SET bikemode="" ' \
          'WHERE bikemode="pb"',

          'UPDATE raw SET bikemode="" ' \
          'WHERE bikemode="xx"',
          )
    for Q in Qs:
        execute(Q)        
    # Convert node_f_id/t to integer type
    Q = 'SELECT rowid, fnode, tnode, ' \
        'leftadd1, leftadd2, rgtadd1, rgtadd2 ' \
        'FROM raw'
    execute(Q)
    rows = cur.fetchall()
    Q = 'UPDATE raw SET fnode=%s, tnode=%s, ' \
        'leftadd1=%s, leftadd2=%s, rgtadd1=%s, rgtadd2=%s ' \
        'WHERE rowid=%s'
    for row in rows:
        cur.execute(Q % (int(row[1]), int(row[2]), int(row[3]),
                         int(row[4]), int(row[5]),
                         int(row[6]), row[0]))  
    con.commit()

def unifyAddressRanges():
    #'LEFTADD1', 'LEFTADD2', 'RGTADD1', 'RGTADD2'
    """Combine left and right side address number into a single value."""
    Q = 'UPDATE raw ' \
        'SET addr_%s=(ROUND(%sadd%s / 10.0) * 10) ' \
        'WHERE %sadd%s != 0'
    for f in (('1', 'f'), ('2', 't')):
        for l in ('left', 'rgt'):
            execute(Q % (f[1], l, f[0], l, f[0]))
    Qs = ('UPDATE raw SET addr_f = (addr_f + (leftadd1 % 2)) ' \
          'WHERE leftadd1 != 0 AND (addr_f % 2 = 0)',

          'UPDATE raw SET addr_f = (addr_f + (1 - (rgtadd1 % 2))) ' \
          'WHERE rgtadd1 != 0 AND (addr_f % 2 = 0)',

          'UPDATE raw SET addr_f = (addr_f + (leftadd2 % 2)) ' \
          'WHERE leftadd2 != 0 AND (addr_f % 2 = 0)',

          'UPDATE raw SET addr_f = (addr_f + (1 - (rgtadd2 % 2))) ' \
          'WHERE rgtadd2 != 0 AND (addr_f % 2 = 0)')
    for Q in Qs:
        execute(Q)
    con.commit()

def transferStreetNames():
    """Transfer street names to their own table."""
    Q = 'INSERT INTO streetname (prefix, name, type, suffix) '\
        'SELECT DISTINCT fdpre, fname, ftype, fdsuf FROM raw'
    execute(Q)
    con.commit()

def updateRawStreetNameIds():
    """Set the street name ID of each raw record."""
    # Get all the distinct street names NEW
    Q = 'SELECT DISTINCT fdpre, fname, ftype, fdsuf FROM raw'
    execute(Q)
    rows = cur.fetchall()
    # Index each street name ID by its street name
    # {(stname)=>streetname_id}
    stnames = {}
    Q = 'SELECT id, prefix, name, type, suffix FROM streetname'
    execute(Q)
    for row in cur.fetchall():
        stnames[(row[1],row[2],row[3],row[4])] = row[0]
    # Index raw row IDs by their street name ID {streetname_id=>[row IDs]}
    stid_rawids = {}
    Q  = 'SELECT rowid, fdpre, fname, ftype, fdsuf FROM raw'
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
        'SELECT DISTINCT lcity FROM raw'
    execute(Q)
    Q = 'INSERT INTO city (city) ' \
        'SELECT DISTINCT rcity FROM raw WHERE rcity NOT IN ' \
        '(SELECT city FROM city)'
    execute(Q)
    con.commit()

def updateRawCityIds():
    """Set the city ID of each raw record."""
    for side in ('l', 'r'):
        Q0 = 'SELECT DISTINCT id, city FROM city'
        Q1 = 'UPDATE raw SET city_%s_id=%s WHERE %scity="%s"' % \
             (side, '%s', side, '%s')
        # Get all the distinct city names
        execute(Q0)
        rows = cur.fetchall()
        # Iterate over city rows and set city IDs of raw records
        met = meter.Meter()
        met.setNumberOfItems(len(rows))
        met.startTimer()
        record_number = 1
        for row in rows:
            execute(Q1 % (row[0], row[1]))
            met.update(record_number)
            record_number+=1
        print  # newline after the progress meter
    con.commit()
    # Convert abbreviated names to full names
    from cities import metro_full_cities
    Q = 'UPDATE city SET city="%s" WHERE city="%s"'
    for c in metro_full_cities:
        execute(Q % (metro_full_cities[c], c))

def updateRawStateIds():
    """Set the state ID of each raw record."""
    Q = 'INSERT INTO state VALUES ("or", "oregon")'
    execute(Q)
    Q = 'UPDATE raw SET state_l_id="or", state_r_id="or"'
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
                execute(Q3 % (node_id, ('point (%.6f %.6f)' % (p.x, p.y))))
            i = -1
    con.commit()

def transferAttrs():
    ## Transfer core attributes to street table
    Q = 'INSERT INTO layer_street ' \
        'SELECT NULL, %s ' \
        'FROM raw' % \
        (','.join(layer_fields))
    execute(Q)

    ## Transfer extra attributes to attributes table (attrs)
    Q = 'INSERT INTO attr_street ' \
        'SELECT NULL, %s ' \
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
    # DB connection and cursor
    con, cur = None, None
    
    # This timer gets reused in the functions above
    timer = meter.Timer()    
    timer.start('Transferring data into byCycle schema...')

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

    for p in pairs[:]:
        msg, func = p[0], p[1]
        try: args = p[2]
        except IndexError: args = ()
        timer.start(msg)
        print msg
        apply(func, args)
        timer.stop()

    timer.stop()
    print 'Done.'

