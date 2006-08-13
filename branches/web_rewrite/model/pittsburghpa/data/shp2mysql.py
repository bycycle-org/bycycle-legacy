# Pittsburgh shapefile import
import sys, os
from pysqlite2 import dbapi2 as sqlite
from byCycle.lib import gis, meter



dbf_fields = ('FNODE_', 'TNODE_',
              'PREFIX', 'NAME', 'TYPE', 'SUFFIX',
                # 'FDPRE', 'FNAME', 'FTYPE', 'FDSUF'
              'LEFTADD1', 'LEFTADD2', 'RGTADD1', 'RGTADD2',
              # 'LCITY', 'RCITY', 'ZIPCOLEF', 'ZIPCORGT',
               'ZIPLEFT', 'ZIPRGT', 'CFCC',
            'ONEWAY', 'OPDIR')#, '?BIKEMODE', 'UP_FRAC', 'ABS_SLP', 'CPD')


layer_fields = ('fnode_', 'tnode_',
                'addr_f', 'addr_t', 'streetname_id', 'city_l_id', 'city_r_id',
                'state_l_id', 'state_r_id', 'zipleft', 'ziprgt', 'wkt_geometry')
attr_fields = ('oneway', 'cfcc', 'opdir')


# DB connection and cursor
con, cur = None, None

def shpToRawSql():
    try:
        os.unlink('raw.db')
        os.unlink('raw.db-journal')
    except OSError, e:
        print e

    datasource = 'files'
    inlayer = 'streetntProjected4'
    #inlayer = 'street4269'
    #inlayer = 'streetnt'
    #inlayer = 'streetntLATLONG'
    outdb = 'raw.db'
    outtable = 'raw'
    outsrs = ''  #'-t_srs WGS84'
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

def fixRaw():
    

    ## Add missing columns
    Q = 'ALTER TABLE raw ADD COLUMN %s'
    cols = ('addr_f', 'addr_t', 'streetname_id', 'city_l_id', 'city_r_id',
            'state_l_id', 'state_r_id', 'code')
    for col in cols:
        execute(Q % col)
    ## Import missing street types field



 ## Set TEXT NULLs to '' and all TEXT values to lower case
    Q0 = 'UPDATE raw SET %s="" WHERE %s IS NULL'
    Q1 = 'UPDATE raw SET %s=lower(%s)'

    cols = ('prefix', 'name', 'type', 'suffix', #'cityl ', 'cityr',
           # 'state_l_id', 'state_r_id',
            'wkt_geometry', 'cfcc',
            #'oneway', 'opdir'
            #, 'bike_facil'
            )
    
    for col in cols:
        # TEXT NULL to ''
        execute(Q0 % (col, col))
        # TEXT to lower
        execute(Q1 % (col, col))
    con.commit()

    # Set BOOLEAN NULLs to f
    Q = 'UPDATE raw SET %s="n" WHERE %s IS NULL'
    cols = ('oneway', 'opdir')
    
    for col in cols:
        execute(Q % (col, col))
        execute(Q1 % (col, col)) 
    con.commit()


    # Set INTEGER NULLs to 0
    Q = 'UPDATE raw SET %s=0 WHERE %s IS NULL'

    cols = ('fnode_', 'tnode_',
            'addr_f', 'addr_t', 'leftadd1', 'leftadd2', 'rgtadd1', 'rgtadd2',
            'streetname_id', 'city_l_id', 'city_r_id', 'zipleft', 'ziprgt'
            #'tlid', 'lanes', 'adt', 'spd',
            #'oneway', 'opdir'
            )
    for col in cols:
        execute(Q % (col, col))
    con.commit()



    
    # Abbreviate bike modes
   # Qs = ('UPDATE raw SET bike_facil="t" ' \
    #      'WHERE bike_facil="bike trail"',
     #     'UPDATE raw SET bike_facil="r" ' \
      #    'WHERE bike_facil="bike route"',
       #   'UPDATE raw SET bike_facil="l" ' \
        #  'WHERE bike_facil="bike lane"',
         # 'UPDATE raw SET bike_facil="p" ' \
          #'WHERE bike_facil="preferred street"',
         # 'UPDATE raw SET cfcc="a71" ' \
         # 'WHERE bike_facil="bt"',
         # )
   # for Q in Qs:
    #    execute(Q)

    #because one piece of data is screwed up & has random j.
    Q = 'UPDATE raw SET rgtadd1="1016" WHERE rgtadd1="1016j"'
    execute(Q)
   # con.commit()
    # Convert fraddl et al to integer type
#    Q = 'SELECT rowid, leftadd1, leftadd2, rgtadd1, rgtadd2 FROM raw'
 #   execute(Q)
  #  rows = cur.fetchall()
    #Q = 'UPDATE raw ' \
     #   'SET leftadd1=%s,leftadd2=%s,rgtadd1=%s,rgtadd2=%s' \
      #  'WHERE rowid=%s'
    #for row in rows:
     #   execute(Q % (int(float(row[1])), int(float(row[2])),
      #                 int(float(row[3])), int(float(row[4])),
       ##               # int(float(row[5])),
         #              row[0]))



   
#        print 'row 2 type: '
 #       print type(row[2])
  #      print row[2]
   #     print 'encoded'
    #    blah = row[2].encode()
     #   print blah
      #  print type(blah)
       # blahInt = int(blah)
        #print type(blahInt)
   
        
   
   



    
    Q = 'SELECT rowid, fnode_, tnode_, leftadd1, leftadd2, rgtadd1, rgtadd2 FROM raw'
    execute(Q)
    rows = cur.fetchall()
    Q = 'UPDATE raw ' \
        'SET fnode_=%s,tnode_=%s,leftadd1=%s,leftadd2=%s,rgtadd1=%s,rgtadd2=%s' \
        'WHERE rowid=%s'
    for row in rows:
        execute(Q % (int(float(row[1])), int(float(row[2])),
                       int(float(row[3])), int(float(row[4])),
                       int(float(row[5])), int(float(row[6])),
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

#    for f in (('f', 'fr'), ('t', 'to')):
 #       for l in ('l', 'r')
    
    for f in (('f', '1'), ('t', '2')):
        for l in ('left', 'rgt'):
            #execute(Q % (f[0], f[1], l, f[1], l))
            execute(Q % (f[0], l, f[1], l, f[1]))


            
    # Encode from address

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
        'SELECT DISTINCT prefix, name, type, suffix FROM raw'
    execute(Q)
    con.commit()

def updateRawStreetNameIds():
    """Set the street name ID of each raw record."""
    # Get all the distinct street names
    Q = 'SELECT DISTINCT prefix, name, type, suffix FROM raw'
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
    Q  = 'SELECT rowid, prefix, name, type, suffix FROM raw'
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
        'Pittsburgh'
        #'SELECT DISTINCT cityl FROM raw'
    execute(Q)
    #Q = 'INSERT INTO city (city) ' \
     #   'SELECT DISTINCT cityr FROM raw WHERE cityr NOT IN ' \
      #  '(SELECT city FROM city)'
    #execute(Q)
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


def updateSimpleCity():
    """Set the city ID of each raw record."""
    Q = 'INSERT INTO city VALUES (1, "pittsburgh")'
    execute(Q)
    Q = 'UPDATE raw SET city_l_id="1", city_r_id="1"'
    execute(Q)
    con.commit()

def updateRawStateIds():
    """Set the state ID of each raw record."""
    Q = 'INSERT INTO state VALUES ("pa", "pennsylvania")'
    execute(Q)
    Q = 'UPDATE raw SET state_l_id="pa", state_r_id="pa"'
    execute(Q)
    con.commit()

def createNodes():
    Q1 = 'SELECT rowid, fnode_, tnode_, wkt_geometry FROM raw'
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
    Q = 'INSERT INTO db.layer_street ' \
        'SELECT rowid, %s ' \
        'FROM raw' % \
        (','.join(layer_fields))
    execute(Q)
    ## Transfer extra attributes to attributes table (attrs)
    Q = 'INSERT INTO db.attr_street ' \
        'SELECT rowid, %s ' \
        'FROM raw' % \
        (','.join(attr_fields))
    execute(Q)
    con.commit()


def addIndexes():
    Qs = ('CREATE INDEX db.addr_f on layer_street (addr_f)',
          'CREATE INDEX db.addr_t on layer_street (addr_t)',
          'CREATE INDEX db.node_f_id on layer_street (node_f_id)',
          'CREATE INDEX db.node_t_id on layer_street (node_t_id)',
          'CREATE INDEX db.stid on layer_street (streetname_id)',
          'VACUUM',
         # 'ANALYZE',
          )
    for Q in Qs: 
        execute(Q)
    
def cleanUp():
    try:
        cur.close()
        con.close()
    except AttributeError:
        print 'Failed: Closing of database (database not open)'

def execute(Q):
    if cur is None:
        openDB()
    try:
        print 'Executing: "%s"' % Q
        cur.execute(Q)
    except Exception, e:
        print 'Failed: %s\n\t%s' % (Q, e)
        sys.exit()

def openDB():
    ## Set up DB connection
    global con, cur
    con = sqlite.connect('raw.db')
    cur = con.cursor()
    Q = 'ATTACH DATABASE "db.db" AS db'
    execute(Q)    

def run():
    overall_timer = meter.Timer()
    overall_timer.start()

    # This timer gets reused in the functions above
    timer = meter.Timer()    
    timer.start()
    
    print 'Transferring data into byCycle schema...\n' \
          '----------------------------------------' \
          '----------------------------------------'

    pairs = [('Convert shapefile to monolithic SQL table',
              shpToRawSql),

             ('Create byCycle schema tables',
             os.system, ('sqlite3 db.db < ./schema.sql',)),
  #           os.system, ('sqlite db.db < ./schema.sql',)),

             ('Open DB connection', openDB),
    
             ('Fix raw table: Remove NULLs, add columns, etc',
              fixRaw),
             
             ('Unify address ranges',
              unifyAddressRanges),

             ('Transfer street names',
              transferStreetNames),
             
             ('Update street name IDs in raw table',
              updateRawStreetNameIds),
             
            # ('Transfer city names',
             # transferCityNames),
             
             #('Update city IDs in raw table',
             # updateRawCityIds),

             ('Update one city in raw table',
              updateSimpleCity),
             
             ('Update state IDs in raw table',
              updateRawStateIds),
             
             ('Create nodes',
              createNodes),
             
             ('Transfer attributes',
              transferAttrs),

             ('Add indexes',
              addIndexes),

             ('Clean up',
             cleanUp),
             ]

    for p in pairs:
        msg, func = p[0], p[1]
        try:
            args = p[2]
        except IndexError:
            args = ()
        overall_timer.pause()
        print('test' + msg)
        resp = raw_input('====> %s? ' % msg).strip().lower()
        overall_timer.unpause()
        if resp in ('', 'y'):
            timer.start()
            apply(func, args)
            print timer.stop()

    print '----------------------------------------' \
          '----------------------------------------\n' \
          'Done. %s total.' % overall_timer.stop()

if __name__ == '__main__':
    run()





