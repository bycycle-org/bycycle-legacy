# shp2mysql.py 
#  Portland, OR, shp/dbf import
#   
# AUTHOR 
#  Wyatt Baldwin <wyatt@bycycle.org>
# DATE 
#  January 27, 2006
#  March 25, 2006 [Converted to interactive; Switched from SQLite to MySQL]
# VERSION 
#  0.1
# PURPOSE 
#  Script to import line geometry and associated attributes from a street layer
#  shapefile and import it into a normalized database
# USAGE 
#  python shp2mysql.py
# LICENSE 
#  GNU Public License (GPL)
#  See LICENSE in top-level package directory
# WARRANTY 
#  This program comes with NO warranty, real or implied.
# TODO
#  Turn this into a derived class; create a base class that all regions can use
import sys, os
from byCycle.lib import gis, meter

region = 'portlandor'

dbf_fields = ('LOCALID', 'FNODE', 'TNODE',
              'LEFTADD1', 'LEFTADD2', 'RGTADD1', 'RGTADD2',
              'FDPRE', 'FNAME', 'FTYPE', 'FDSUF',
              'LCITY', 'RCITY', 'ZIPCOLEF', 'ZIPCORGT',
              'ONE_WAY', 'TYPE', 'BIKEMODE', 'UP_FRAC', 'ABS_SLP', 'CPD', 'SSCODE')

layer_fields = ('fnode', 'tnode',
                'addr_f', 'addr_t', 'even_side', 'streetname_id', 'city_l_id', 'city_r_id',
                'state_l_id', 'state_r_id', 'zipcolef', 'zipcorgt',
                'wkt_geometry')

attr_fields = ('localid', 'one_way', 'code', 'bikemode', 'up_frac', 'abs_slp', 'cpd', 'sscode')

# DB handle
db = None
    
def shpToRawSql():
    datasource = '20061219'
    layer = 'new84'
    path = '.'.join((os.path.join(os.getcwd(), datasource, layer), "dbf"))
    fields = ','.join(['IX'] + list(dbf_fields))
    database = 'portlandor'
    table = 'raw'
    primary_key = 'id'
    names = 'IX=ID'
    cmd = ('dbf2mysql -f -l -o %s -s %s -h localhost -d %s -t %s -c -p %s -U root -P "" %s' % 
                (fields, names, database, table, primary_key, path))
    print cmd
    exit_code = os.system(cmd)
    if exit_code:
        sys.exit()
    
def fixRaw():
    # Add missing...    
    # INTEGER columns
    Q = 'ALTER TABLE raw ADD COLUMN %s INTEGER NOT NULL'
    cols = ('addr_f', 'addr_t', 'streetname_id', 'city_l_id', 'city_r_id', 'code', 'sscode')
    for col in cols:
        execute(Q % col)
    # CHAR(s) columns
    Q = 'ALTER TABLE raw ADD COLUMN %s CHAR(2) NOT NULL' 
    cols = ('state_l_id', 'state_r_id', 'wkt_geometry') # wkt is temporary
    for col in cols:
        execute(Q % col)
    # ENUM columns
    execute('ALTER TABLE raw ADD COLUMN even_side ENUM("l", "r") NOT NULL')
    # Temporary merge of type column
    cmd = 'dbf2mysql -f -l -o IX,TYPE -s IX=ID,TYPE=CODE ' \
                '-h localhost -d portlandor -t code -c -p id -U root -P "" ' \
                '/usr/lib/python2.4/site-packages/byCycle/tripplanner/model/portlandor/data/20061219/type.dbf'
    print cmd
    exit_code = os.system(cmd)
    if exit_code:
        sys.exit()
    execute('SELECT id, code FROM code ORDER BY id')
    for i, row in enumerate(db.fetchAll()):
        execute('UPDATE raw SET code = %s WHERE id = %s' % (row[1], row[0]), False)
    # Abbreviate bike modes
    Q = 'UPDATE raw SET bikemode="%s" WHERE bikemode="%s"'
    bm = (("t", "mu"),
          ("p", "mm"),
          ("b", "bl"),
          ("l", "lt"),
          ("m", "mt"),
          ("h", "ht"),
          ("c", "ca"),
          ("x", "pm"),
          ("x", "up"),
          ("", "pb"),
          ("", "xx")
          )
    for m in bm:
        execute(Q % (m[0], m[1]))        

def createSchema():
    tables = ('layer_street', 'attr_street', 'layer_node', 'streetname', 'city', 'state')
    for table in tables:
        execute('DROP TABLE IF EXISTS %s' % table)
    cmd = 'mysql -u root --password="" < ./schema.sql'
    print cmd
    exit_code = os.system(cmd)
    if exit_code:
        sys.exit()
        
def unifyAddressRanges():
    #'LEFTADD1', 'LEFTADD2', 'RGTADD1', 'RGTADD2'
    """Combine left and right side address number into a single value."""
    QF = 'UPDATE raw ' \
        'SET addr_f = (ROUND(%sadd1 / 10.0) * 10) + 1 ' \
        'WHERE %sadd1 != 0'
    QT = 'UPDATE raw ' \
        'SET addr_t = (ROUND(%sadd2 / 10.0) * 10) ' \
        'WHERE %sadd2 != 0'
    for f in ('left', 'rgt'):
        execute(QF % (f, f))
        execute(QT % (f, f))
    # Set even side
    QEL = 'UPDATE raw SET even_side = "l" ' \
          'WHERE (leftadd1 != 0 AND leftadd1 % 2 = 0) OR ' \
          ' (leftadd2 != 0 AND leftadd2 % 2 = 0)'
    QER = 'UPDATE raw SET even_side = "r" ' \
          'WHERE (rgtadd1 != 0 AND rgtadd1 % 2 = 0) OR ' \
          ' (rgtadd2 != 0 AND rgtadd2 % 2 = 0)'
    execute(QEL)
    execute(QER)

def transferStreetNames():
    """Transfer street names to their own table."""
    Q = 'INSERT INTO streetname (prefix, name, type, suffix) '\
        'SELECT DISTINCT fdpre, fname, ftype, fdsuf FROM raw'
    execute(Q)

def updateRawStreetNameIds():
    """Set the street name ID of each raw record."""
    # Get all the distinct street names NEW
    Q = 'SELECT DISTINCT fdpre, fname, ftype, fdsuf FROM raw'
    execute(Q)
    rows = db.fetchAll()
    # Index each street name ID by its street name
    # {(stname)=>streetname_id}
    stnames = {}
    Q = 'SELECT id, prefix, name, type, suffix FROM streetname'
    execute(Q)
    for row in db.fetchAll():
        stnames[(row[1],row[2],row[3],row[4])] = row[0]
    # Index raw row IDs by their street name ID {streetname_id=>[row IDs]}
    stid_rawids = {}
    Q  = 'SELECT id, fdpre, fname, ftype, fdsuf FROM raw'
    execute(Q)
    for row in db.fetchAll():
        stid = stnames[(row[1],row[2],row[3],row[4])]
        if stid in stid_rawids: 
            stid_rawids[stid].append(row[0])
        else: 
            stid_rawids[stid] = [row[0]]
    # Iterate over street name IDs and set street name IDs of raw records
    Q = 'UPDATE raw SET streetname_id=%s WHERE id IN %s'
    met = meter.Meter()
    met.setNumberOfItems(len(stid_rawids))
    met.startTimer()
    record_number = 1
    for stid in stid_rawids:
        ixs = stid_rawids[stid]
        if len(ixs) == 1:
            in_data = '(%s)' % int(ixs[0])
        else:
            in_data = tuple([int(ix) for ix in ixs])
        execute(Q % (stid, in_data), False)
        met.update(record_number)
        record_number+=1
    print  # newline after the progress meter

def transferCityNames():
    """Transfer city names to their own table."""
    Q = 'INSERT INTO city (city) ' \
        'SELECT DISTINCT lcity FROM raw'
    execute(Q)
    Q = 'INSERT INTO city (city) ' \
        'SELECT DISTINCT rcity FROM raw WHERE rcity NOT IN ' \
        '(SELECT city FROM city)'
    execute(Q)

def updateRawCityIds():
    """Set the city ID of each raw record."""
    Q0 = 'SELECT DISTINCT id, city FROM city'
    for side in ('l', 'r'):
        Q1 = 'UPDATE raw SET city_%s_id=%s WHERE %scity="%s"' % \
             (side, '%s', side, '%s')
        # Get all the distinct city names
        execute(Q0)
        rows = db.fetchAll()
        # Iterate over city rows and set city IDs of raw records
        for row in rows:
            execute(Q1 % (row[0], row[1]))
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

def createNodes():
    Q1 = 'SELECT id, fnode, tnode, wkt_geometry FROM raw'
    Q2 = 'UPDATE raw SET wkt_geometry="%s" WHERE id=%s'
    Q3 = 'INSERT INTO layer_node (id, wkt_geometry) VALUES (%s, "%s")'
    seen_node_ids = {}
    # Get node_ids and geometry from raw table
    execute(Q1)
    # Insert node IDs into layer_node, skipping the ones we've already seen
    for row in db.fetchAll():
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

def transferAttrs():
    # Transfer core attributes to street table
    fields = ', '.join(layer_fields)
    Q = 'INSERT INTO layer_street SELECT NULL, %s FROM raw' % fields
    execute(Q)
    # Transfer extra attributes to attributes table (attrs)
    fields = ', '.join(attr_fields)
    Q = 'INSERT INTO attr_street SELECT NULL, %s FROM raw' % fields
    execute(Q)

def addIndexes():
    Qs = ('CREATE INDEX addr_f on layer_street (addr_f)',
          'CREATE INDEX addr_t on layer_street (addr_t)',
          'CREATE INDEX node_f_id on layer_street (node_f_id)',
          'CREATE INDEX node_t_id on layer_street (node_t_id)',
          'CREATE INDEX stid on layer_street (streetname_id)',
          )
    for Q in Qs: 
        execute(Q)
        
def cleanUp():
    pass

def execute(Q, show=True):
    if db is None:
        openDB()
    try:
        if show:
            print 'Executing: "%s"' % Q
        db.execute(Q)
    except Exception, e:
        print 'Execution failed: %s' % e
        sys.exit()

def openDB():
    ## Set up DB connection
    global db
    path = 'byCycle.tripplanner.model.%s' % region
    db = __import__(path, globals(), locals(), ['']).Mode()
 
def run():
    overall_timer = meter.Timer()
    overall_timer.start()

    # This timer gets reused in the functions above
    timer = meter.Timer()    
    timer.start()

    pairs = [
             ('Convert shapefile to monolithic SQL table',
              shpToRawSql),

             ('Fix raw table: Remove NULLs, add columns, etc',
              fixRaw),

              ('Create byCycle schema tables',
              createSchema),
              
             ('Unify address ranges',
              unifyAddressRanges),

             ('Transfer street names',
              transferStreetNames),
             
             ('Update street name IDs in raw table',
              updateRawStreetNameIds),
             
             ('Transfer city names',
              transferCityNames),
             
             ('Update city IDs in raw table',
              updateRawCityIds),
             
             ('Update state IDs in raw table',
              updateRawStateIds),
             
             ('Create nodes',
              createNodes),
             
             ('Transfer attributes',
              transferAttrs),

             ('Add indexes',
              addIndexes),
             ]

    start = -1
    no_prompt = False
    only = False
    try:
        arg1 = sys.argv[1]
    except IndexError:
      pass
    else: 
        try:
            start = int(arg1)
        except ValueError:
            no_prompt = arg1 == 'no_prompt'
        else:
            try:
                arg2 = sys.argv[2]
            except IndexError:
                pass
            else:
                only = arg2 == "only"
  
    print 'Transferring data into byCycle schema...\n' \
          '----------------------------------------' \
          '----------------------------------------'
    prompt = '====>'
    if only:
        pair = pairs[start]
        msg, func = pair[0], pair[1]
        print '%s %s' % (prompt, msg)
        try:
            args = pair[2]
        except IndexError:
            args = ()
        timer.start()
        apply(func, args)
        print timer.stop()
    else:
        for i, p in enumerate(pairs):
            msg, func = p[0], p[1]
            if i < start:
                print '%s Skipping %s %s? ' % (i, prompt, msg)
                continue
            try:
                args = p[2]
            except IndexError:
                args = ()
            sys.stdout.write('%s %s %s'% (i, prompt, msg))
            if not no_prompt:
                overall_timer.pause()
                resp = raw_input('? ').strip().lower()
                overall_timer.unpause()
            else:
                print
            if  no_prompt or resp in ('', 'y'):
                timer.start()
                apply(func, args)
                print timer.stop()

    print '----------------------------------------' \
          '----------------------------------------\n' \
          'Done. %s total.' % overall_timer.stop()

if __name__ == '__main__':
    run()
