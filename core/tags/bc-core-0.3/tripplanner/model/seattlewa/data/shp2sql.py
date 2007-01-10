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
#  Note: Run from the region/data directory
# LICENSE 
#  GNU Public License (GPL)
#  See LICENSE in top-level package directory
# WARRANTY 
#  This program comes with NO warranty, real or implied.
# TODO
#  Turn this into a derived class; create a base class that all regions can use
import sys, os

sys.path.append('/home/dacc/proj/bycycle')

from byCycle.lib import gis, meter


CWD = os.getcwd()


# -- Edit variables for region

BYCYCLE_PATH = '/home/dacc/proj/bycycle/byCycle'

region = 'seattlewa'

# Full path to mysqlgisimport executable
mysqlgisimport = 'mysqlgisimport'

# Directory containing shp/dbf files
datasource = '.'
# shp/dbf base name
layer = 'snd'

# Fields we want from the DBF
dbf_fields = ('FNODE',
              'TNODE',
              'L_ADD_FROM',
              'L_ADD_TO',
              'R_ADD_FROM',
              'R_ADD_TO',
              'PREDIR',
              'STREETNAM',
              'STREETTYP',
              'SUFDIR',

              # rolling LCITY and RCITY into CITY.
              'CITY',
              'CITY',

              'LZIP',
              'RZIP',

              # unique edge id
              'SNDID',

              # bike desgination
              'BIKECLASS'

              # cutting for now: need to join to the oneway.dbf shapefile using
              # SNDID to get this.
#              'ONE_WAY',

              # fraction of edge that's uphill.  not currently sure whether or
              # not this is available.
#              'UP_FRAC',
#              'ABS_SLP',

              # cars per day.  may or may not be available.
#              'CPD',
)

# Fields in raw table to be transferred to street layer table.
# The items in this list must correspond to the fields in the street layer
# table definition (i.e., must be in the right order).
db_fields = ('geo',
             'fnode_',
             'tnode_',
             'addr_f',
             'addr_t',
             'even_side',
             'street_name_id',
             'city_l_id',
             'city_r_id',
             'state_l_id',
             'state_r_id',
             'l_zip',
             'r_zip',
             'snd_id',
             'bikeclass'
            )

db_name = 'ByCycleSandbox'
db_user = 'dacc'
#path = os.path.join(BYCYCLE_PATH, 'tripplanner/model/.pw')
#db_pass = open(path).read().strip()
db_pass = ''

state_id = 'wa'
state = 'washington'

# -- End edit variables for region


# Command-line args
start = -1
no_prompt = True
only = False

# DB handle
db = None

# Name of table for mysqlgisimport to import into
raw = '%s_raw' % region

# Timer object
timer = None

    
def shpToRawSql():
    path = os.path.join(CWD, datasource, layer)
    # Drop existing raw table
    Q = 'DROP TABLE IF EXISTS %s' % raw
    if not _wait(Q):
        _execute(Q)
    # Extract SQL from Shapefile
    cmd = '%s -t %s -o %s.sql %s' % \
          (mysqlgisimport, raw, raw, path)
    if not _wait('Extract SQL from Shapefile'):
        _system(cmd)
    # Load SQL into DB
    cmd = 'mysql -u %s --password="%s" %s < %s.sql' % \
          (db_user, db_pass, db_name, raw)
    if not _wait('Load SQL into DB'):
        _system(cmd)
        
def addColumns():
    # INTEGER columns
    Q = 'ALTER TABLE %s ADD COLUMN %%s %%s NOT NULL' % raw
    cols = ('addr_f', 'addr_t', 'street_name_id', 'city_l_id', 'city_r_id')
    for col in cols:
        _execute(Q % (col, 'INTEGER'))
    # TINY INTEGER columns
    Q = 'ALTER TABLE %s ADD COLUMN %%s %%s NOT NULL' % raw
    cols = ('one_way_enc',)
    for col in cols:
        _execute(Q % (col, 'TINYINT'))
    # CHAR(s) columns
    cols = ('state_l_id', 'state_r_id')
    for col in cols:
        _execute(Q % (col, 'CHAR(2)'))
    # ENUM columns
    _execute(Q % ('even_side', 'ENUM("l", "r")'))

def encodeOneWays():
    # Set unknown one_ways to 0
    Q = 'UPDATE %s SET one_way_enc = 0 WHERE one_way NOT IN (%s)' % \
        (raw, ', '.join(['"%s"' % ow for ow in one_ways.keys()]))
    _execute(Q)
    # Encode one ways
    Q = 'UPDATE %s SET one_way_enc = %%s WHERE one_way = "%%s"' % raw
    for ow in one_ways:
        _execute(Q % (one_ways[ow], ow))

def updateBikeModes():
    # Set unknown bikemodes to x
    Q = 'UPDATE %s SET bikemode = "x" WHERE bikemode NOT IN (%s)' % \
        (raw, ', '.join(['"%s"' % bm for bm in bikemodes.keys()]))
    _execute(Q)
    # Abbreviate bike modes
    Q = 'UPDATE %s SET bikemode = "%%s" WHERE bikemode = "%%s"' % raw
    for bm in bikemodes: 
        _execute(Q % (bikemodes[bm], bm))

def createSchema():
    tables = ('layer_street', 'layer_node', 'streetname', 'city', 'state')
    for table in tables:
        _execute('DROP TABLE IF EXISTS %s_%s' % (region, table))
    cmd = 'mysql -u %s --password="%s" %s < ./schema.sql' % \
          (db_user, db_pass, db_name)
    _system(cmd)
        
def unifyAddressRanges():
    #'LEFTADD1', 'LEFTADD2', 'RGTADD1', 'RGTADD2'
    """Combine left and right side address number into a single value."""
    QF = 'UPDATE %s ' \
        'SET addr_f = (ROUND(%s_add_from / 10.0) * 10) + 1 ' \
        'WHERE %s_add_from != 0'
    QT = 'UPDATE %s ' \
        'SET addr_t = (ROUND(%s_add_to / 10.0) * 10) ' \
        'WHERE %s_add_to != 0'
    for side in ('l', 'r'):
        _execute(QF % (raw, side, side))
        _execute(QT % (raw, side, side))
    # Set even side
    QEL = 'UPDATE %s SET even_side = "l" ' \
          'WHERE (l_add_from != 0 AND l_add_from %% 2 = 0) OR ' \
          ' (l_add_to != 0 AND l_add_to %% 2 = 0)'
    QER = 'UPDATE %s SET even_side = "r" ' \
          'WHERE (r_add_from != 0 AND r_add_from %% 2 = 0) OR ' \
          ' (r_add_to != 0 AND r_add_to %% 2 = 0)'
    _execute(QEL % raw)
    _execute(QER % raw)

def transferStreetNames():
    """Transfer street names to their own table."""

    Q = 'UPDATE %s SET pre_dir = LOWER(pre_dir), street_nam = LOWER(street_nam),'\
        'street_typ = LOWER(street_typ), suf_dir = LOWER(suf_dir)'
    _execute(Q % (raw))

    Q = 'INSERT INTO %s_streetname (prefix, name, sttype, suffix) '\
        'SELECT DISTINCT LOWER(pre_dir), LOWER(street_nam), LOWER(street_typ), LOWER(suf_dir) FROM %s'
    _execute(Q % (region, raw))

def updateRawStreetNameIds():
    """Set the street name ID of each raw record."""
    # Get all the distinct street names
    Q = 'SELECT DISTINCT pre_dir, street_nam, street_typ, suf_dir FROM %s' % raw
    _execute(Q)
    rows = db.fetchAll()
    # Index each street name ID by its street name
    # {(stname)=>street_name_id}
    stnames = {}
    Q = 'SELECT id, prefix, name, sttype, suffix FROM %s_streetname' % region
    _execute(Q)
    for row in db.fetchAll():
        stnames[(row[1],row[2],row[3],row[4])] = row[0]
    # Index raw row IDs by their street name ID {street_name_id=>[row IDs]}
    stid_rawids = {}
    Q  = 'SELECT id, pre_dir, street_nam, street_typ, suf_dir FROM %s' % raw
    _execute(Q)
    for row in db.fetchAll():
        stid = stnames[(row[1],row[2],row[3],row[4])]
        if stid in stid_rawids: 
            stid_rawids[stid].append(row[0])
        else: 
            stid_rawids[stid] = [row[0]]
    # Iterate over street name IDs and set street name IDs of raw records
    Q = 'UPDATE %s SET street_name_id=%%s WHERE id IN %%s' % raw
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
        'SELECT DISTINCT city FROM %s' % (region, raw)
    _execute(Q)
    Q = 'INSERT INTO %s_city (city) ' \
        'SELECT DISTINCT city FROM %s WHERE city NOT IN ' \
        '(SELECT city FROM %s_city)' % (region, raw, region)
    _execute(Q)

def updateRawCityIds():
    """Set the city ID of each raw record."""
    Q0 = 'SELECT DISTINCT id, city FROM %s_city' % region
    for side in ('l', 'r'):
        Q1 = 'UPDATE %s SET city_%s_id=%s WHERE city="%s"' % \
             (raw, side, '%s', side, '%s')
        # Get all the distinct city names
        _execute(Q0)
        rows = db.fetchAll()
        # Iterate over city rows and set city IDs of raw records
        for row in rows:
            _execute(Q1 % (row[0], row[1]))
    # Convert abbreviated city names to full names
    from cities import cities_atof
    Q = 'UPDATE %s_city SET city="%s" WHERE city="%s"'
    for c in cities_atof:
        _execute(Q % (region, cities_atof[c], c.upper()))

def updateRawStateIds():
    """Set the state ID of each raw record."""
    Q = 'INSERT INTO %s_state VALUES ("%s", "%s")' % \
        (region, state_id, state)
    _execute(Q)
    Q = 'INSERT INTO %s_state VALUES ("wa", "washington")' % region
    _execute(Q)
    Q = 'UPDATE %s SET state_l_id = "%s", state_r_id = "%s"' % \
        (raw, state_id, state_id)
    _execute(Q)
    
    Q = 'SELECT id FROM seattlewa_city WHERE city = "vancouver"'
    _execute(Q)
    global db
    the_couv_id = db.fetchRow()[0]

    Q = 'UPDATE %s SET state_l_id = "%s" WHERE city_l_id = %s' % \
        (raw, 'wa', the_couv_id)
    _execute(Q)
    Q = 'UPDATE %s SET state_r_id = "%s" WHERE city_r_id = %s' % \
        (raw, 'wa', the_couv_id)
    _execute(Q)

def setCityState():
  # there is only one city and state covered by this region
  _execute('UPDATE seattlewa_layer_street SET city_l_id = 1, city_r_id = 1,'\
      'state_l_id = 1, state_r_id = 1')

def createNodes():
    Q = 'INSERT INTO %s_layer_node ' \
        '(SELECT DISTINCT fnode_, startpoint(geo)' \
        ' FROM %s)' % (region, raw)
    _execute(Q)    
    Q = 'INSERT INTO %s_layer_node ' \
        '(SELECT DISTINCT tnode_, endpoint(geo)' \
        ' FROM %s' \
        ' WHERE tnode_ NOT IN (SELECT DISTINCT id FROM %s_layer_node))' % \
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
            print 'Executing: %s' % Q
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

#             ('Encode one ways',
#             encodeOneWays),
    
#             ('Update bike modes in raw table',
#              updateBikeModes),
             
             ('Create byCycle schema tables',
              createSchema),
             
             ('Unify address ranges',
              unifyAddressRanges),
             
             ('Transfer street names',
              transferStreetNames),
             
             ('Update street name IDs in raw table',
              updateRawStreetNameIds),
             
#             ('Transfer city names',
#              transferCityNames),
             
#             ('Update city IDs in raw table',
#              updateRawCityIds),
             
#             ('Update state IDs in raw table',
#              updateRawStateIds),

             ('Set city and State',
               setCityState),

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
