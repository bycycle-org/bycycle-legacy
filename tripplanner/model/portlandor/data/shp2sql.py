# shp2mysql.py 
#  Portland, OR, shp/dbf import
#   
# AUTHOR 
#  Wyatt Baldwin <wyatt@bycycle.org>
# DATE 
#  January 27, 2006
#  March 25, 2006 [Converted to interactive; Switched from SQLite to MySQL]
#  April 4, 2006 [Converted to single-DB, shared with other regions]
# VERSION 
#  0.1
# PURPOSE 
#  Script to import line geometry and associated attributes from a street layer
#  shapefile into a normalized database
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


# Fields we want from the DBF
dbf_fields = ('FNODE',
              'TNODE',
              'LEFTADD1',
              'LEFTADD2',
              'RGTADD1',
              'RGTADD2',
              'FDPRE',
              'FNAME',
              'FTYPE',
              'FDSUF',
              'LCITY',
              'RCITY',
              'ZIPCOLEF',
              'ZIPCORGT',
              'LOCALID',
              'ONE_WAY',
              'TYPE',
              'BIKEMODE',
              'UP_FRAC',
              'ABS_SLP',
              'CPD',
              'SSCODE')

# Fields in raw table to be transferred to street layer table.
# The items in this list must correspond to the fields in the street layer
# table definition (i.e., must be in the right order).
db_fields = ('geo',
             'fnode',
             'tnode',
             'addr_f',
             'addr_t',
             'even_side',
             'streetname_id',
             'city_l_id',
             'city_r_id',
             'state_l_id',
             'state_r_id',
             'zipcolef',
             'zipcorgt',
             'localid',
             'one_way',
             'type',
             'bikemode',
             'up_frac',
             'abs_slp',
             'cpd',
             'sscode')

# Command-line args
start = -1
no_prompt = False
only = False

# DB handle
db = None

raw = '%s_raw' % region

timer = None

    
def shpToRawSql():
    datasource = '20061219'
    layer = 'new1'
    path = os.path.join(os.getcwd(), datasource)
    # Drop existing raw table
    Q = 'DROP TABLE IF EXISTS %s' % raw
    if not _wait(Q):
        _execute(Q)
    # Extract SQL from Shapefile
    cmd = 'mysqlgisimport -t %s -o %s.sql %s' % \
          (raw, raw, os.path.join(path, layer))
    if not _wait('Extract SQL from Shapefile'):
        _system(cmd)
    # Load SQL into DB
    cmd = 'mysql -u root --password="" bycycle-1 < %s.sql' % raw
    if not _wait('Load SQL into DB'):
        _system(cmd)
        
def addColumns():
    # Add missing...    
    # INTEGER columns
    Q = 'ALTER TABLE %s ADD COLUMN %%s %%s NOT NULL' % raw
    cols = ('addr_f', 'addr_t', 'streetname_id', 'city_l_id', 'city_r_id')
    for col in cols:
        _execute(Q % (col, 'INTEGER'))
    # CHAR(s) columns
    cols = ('state_l_id', 'state_r_id')
    for col in cols:
        _execute(Q % (col, 'CHAR(2)'))
    # ENUM columns
    _execute(Q % ('even_side', 'ENUM("l", "r")'))

def fixRaw():
    # Abbreviate bike modes
    Q = 'UPDATE %s SET bikemode="%%s" WHERE bikemode="%%s"' % raw
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
        _execute(Q % (m[0], m[1]))        

def createSchema():
    tables = ('layer_street', 'layer_node', 'streetname', 'city', 'state')
    for table in tables:
        _execute('DROP TABLE IF EXISTS %s_%s' % (region, table))
    cmd = 'mysql -u root --password="" < ./schema.sql'
    _system(cmd)
        
def unifyAddressRanges():
    #'LEFTADD1', 'LEFTADD2', 'RGTADD1', 'RGTADD2'
    """Combine left and right side address number into a single value."""
    QF = 'UPDATE %s ' \
        'SET addr_f = (ROUND(%sadd1 / 10.0) * 10) + 1 ' \
        'WHERE %sadd1 != 0'
    QT = 'UPDATE %s ' \
        'SET addr_t = (ROUND(%sadd2 / 10.0) * 10) ' \
        'WHERE %sadd2 != 0'
    for side in ('left', 'rgt'):
        _execute(QF % (raw, side, side))
        _execute(QT % (raw, side, side))
    # Set even side
    QEL = 'UPDATE %s SET even_side = "l" ' \
          'WHERE (leftadd1 != 0 AND leftadd1 %% 2 = 0) OR ' \
          ' (leftadd2 != 0 AND leftadd2 %% 2 = 0)'
    QER = 'UPDATE %s SET even_side = "r" ' \
          'WHERE (rgtadd1 != 0 AND rgtadd1 %% 2 = 0) OR ' \
          ' (rgtadd2 != 0 AND rgtadd2 %% 2 = 0)'
    _execute(QEL % raw)
    _execute(QER % raw)

def transferStreetNames():
    """Transfer street names to their own table."""
    Q = 'INSERT INTO %s_streetname (prefix, name, type, suffix) '\
        'SELECT DISTINCT fdpre, fname, ftype, fdsuf FROM %s'
    _execute(Q % (region, raw))

def updateRawStreetNameIds():
    """Set the street name ID of each raw record."""
    # Get all the distinct street names NEW
    Q = 'SELECT DISTINCT fdpre, fname, ftype, fdsuf FROM %s' % raw
    _execute(Q)
    rows = db.fetchAll()
    # Index each street name ID by its street name
    # {(stname)=>streetname_id}
    stnames = {}
    Q = 'SELECT id, prefix, name, type, suffix FROM %s_streetname' % region
    _execute(Q)
    for row in db.fetchAll():
        stnames[(row[1],row[2],row[3],row[4])] = row[0]
    # Index raw row IDs by their street name ID {streetname_id=>[row IDs]}
    stid_rawids = {}
    Q  = 'SELECT id, fdpre, fname, ftype, fdsuf FROM %s' % raw
    _execute(Q)
    for row in db.fetchAll():
        stid = stnames[(row[1],row[2],row[3],row[4])]
        if stid in stid_rawids: 
            stid_rawids[stid].append(row[0])
        else: 
            stid_rawids[stid] = [row[0]]
    # Iterate over street name IDs and set street name IDs of raw records
    Q = 'UPDATE %s SET streetname_id=%%s WHERE id IN %%s' % raw
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
        _execute(Q % (stid, in_data), False)
        met.update(record_number)
        record_number+=1
    print  # newline after the progress meter

def transferCityNames():
    """Transfer city names to their own table."""
    Q = 'INSERT INTO %s_city (city) ' \
        'SELECT DISTINCT lcity FROM %s' % (region, raw)
    _execute(Q)
    Q = 'INSERT INTO %s_city (city) ' \
        'SELECT DISTINCT rcity FROM %s WHERE rcity NOT IN ' \
        '(SELECT city FROM %s_city)' % (region, raw, region)
    _execute(Q)

def updateRawCityIds():
    """Set the city ID of each raw record."""
    Q0 = 'SELECT DISTINCT id, city FROM %s_city' % region
    for side in ('l', 'r'):
        Q1 = 'UPDATE %s SET city_%s_id=%s WHERE %scity="%s"' % \
             (raw, side, '%s', side, '%s')
        # Get all the distinct city names
        _execute(Q0)
        rows = db.fetchAll()
        # Iterate over city rows and set city IDs of raw records
        for row in rows:
            _execute(Q1 % (row[0], row[1]))
    # Convert abbreviated names to full names
    from cities import metro_full_cities
    Q = 'UPDATE %s_city SET city="%s" WHERE city="%s"'
    for c in metro_full_cities:
        _execute(Q % (region, metro_full_cities[c], c.upper()))

def updateRawStateIds():
    """Set the state ID of each raw record."""
    Q = 'INSERT INTO %s_state VALUES ("or", "oregon")' % region
    _execute(Q)
    Q = 'UPDATE %s SET state_l_id="or", state_r_id="or"' % raw
    _execute(Q)

def createNodes():
    Q = 'INSERT INTO %s_layer_node ' \
        '(SELECT DISTINCT fnode, startpoint(geo)' \
        ' FROM %s)' % (region, raw)
    _execute(Q)    
    Q = 'INSERT INTO %s_layer_node ' \
        '(SELECT DISTINCT tnode, endpoint(geo)' \
        ' FROM %s' \
        ' WHERE tnode NOT IN (SELECT DISTINCT id FROM %s_layer_node))' % \
        (region, raw, region)
    _execute(Q)

def transferAttrs():
    """Transfer fields from raw table to street layer table."""
    fields = ', '.join(db_fields)
    Q = 'INSERT INTO %s_layer_street SELECT NULL, %s FROM %s' % \
        (region, fields, raw)
    _execute(Q)


## --

def _system(cmd):
    print cmd
    exit_code = os.system(cmd)
    if exit_code:
        sys.exit()

def _wait(msg='Continue or skip'):
    if no_prompt:
        return False
    timer.pause()
    resp = raw_input(msg + '? ')
    timer.unpause()
    return resp

def _openDB():
    """Set up DB connection."""
    global db
    path = 'byCycle.tripplanner.model.%s' % region
    db = __import__(path, globals(), locals(), ['']).Mode()
 
def _execute(Q, show=True):
    """Execute a SQL query."""
    if db is None:
        _openDB()
    try:
        if show:
            print 'Executing: "%s"' % Q
        db.execute(Q)
    except Exception, e:
        print 'Execution failed: %s' % e
        sys.exit()

def run():
    global start, only, no_prompt, timer
    
    overall_timer = meter.Timer()
    overall_timer.start()

    # Reset for each function
    timer = meter.Timer(start_now=False)    

    pairs = [('Convert shapefile to monolithic SQL table',
              shpToRawSql),

             ('Add columns to raw',
              addColumns),
             
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
             ]

    # Process command-line arguments
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
                only = arg2 == 'only'
                no_prompt = arg2 == 'no_prompt'
    do_prompt = not no_prompt
  
    print 'Transferring data into byCycle schema...\n' \
          '----------------------------------------' \
          '----------------------------------------'
    prompt = '====>'
    if only:
        # Do one function without prompting
        pair = pairs[start]
        msg, func = pair[0], pair[1]
        print '%s %s' % (prompt, msg)
        # Get function arguments
        try:
            args = pair[2]
        except IndexError:
            args = ()
        # Do function            
        timer.start() 
        apply(func, args)
        print timer.stop()
    else:
        # Do all functions, starting from specified
        for i, p in enumerate(pairs):
            msg, func = p[0], p[1]
            if i < start:
                # Skip functions before specified starting point
                print '%s Skipping %s %s? ' % (i, prompt, msg)
                continue
            # Get function arguments
            try:
                args = p[2]
            except IndexError:
                args = ()
            # Show prompt and function message
            sys.stdout.write('%s %s %s'% (i, prompt, msg))
            if do_prompt:
                # Prompt user to continue
                overall_timer.pause()
                resp = raw_input('? ').strip().lower()
                overall_timer.unpause()
            else:
                # Don't prompt user to continue
                print
            if  no_prompt or resp in ('', 'y'):
                # Do function
                timer.start()
                apply(func, args)
                print timer.stop()
            elif resp in ('q', 'quit', 'exit'):
                print 'Aborted at %s' % i
                sys.exit()

    print '----------------------------------------' \
          '----------------------------------------\n' \
          'Done. %s total.' % overall_timer.stop()

if __name__ == '__main__':
    run()
