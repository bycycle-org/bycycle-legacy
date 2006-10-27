#!/usr/bin/python
###########################################################################
# $Id: shp2pgsql.py 187 2006-08-16 01:26:11Z bycycle $
# Created 2006-09-07
#
# Portland, OR, shapefile import.
#
# Copyright (C) 2006 Wyatt Baldwin, byCycle.org <wyatt@bycycle.org>.
# All rights reserved.
#
# For terms of use and warranty details, please see the LICENSE file included
# in the top level of this distribution. This software is provided AS IS with
# NO WARRANTY OF ANY KIND.


"""
Usage: shp2pgsql.py [various options]

There are three forms for running this script:
- This will run through all the actions, prompting you for each one:
  shp2pgsql.py

- This will either prompt you to run the actions from indices i to j in the
  actions list or just run all the actions from i to j if `no_prompt` is
  specified:
  shp2pgsql.py [--start|-s <i>] [--end|-e <j>] [--no_prompt|-n]

- This will run only the action at index i without prompting:
  shp2pgsql.py --only|-o <i>

Defaults:
    - start=0
    - end=n-1 where n is the number of actions
    - no_prompt flag off
    - only not used

If no args are supplied, you will be prompted to run all actions.

If either of ``start`` or ``end`` (or both) is present, the ``only`` option
must not be present.

If ``only`` is present, ``no_prompt`` is implied.

"""
import os
def __getbyCycleImportPath():
    """Get path to dir containing the byCycle package this module is part of."""
    path = os.path.abspath(__file__)
    opd = os.path.dirname
    for i in range(5):
        path = opd(path)
    return path

import sys
sys.path.insert(0, __getbyCycleImportPath())
import getopt

import psycopg2
import psycopg2.extensions

import sqlalchemy
from sqlalchemy.sql import func, select, bindparam
from sqlalchemy.schema import Column
from byCycle.model.data.sqltypes import Geometry

from byCycle import install_path
from byCycle.lib import meter
from byCycle.model.portlandor.data.tables import Tables, SRID
from byCycle.model.portlandor.data.cities import cities_atof


### Region Configuration
### Should be the only configuration that gets changed per-region

region = 'portlandor'
srid = 2913

# Target format: /base/path/to/regional_data/specific_region/datasource/layer
# Ex: /home/bycycle/byCycle/data/portlandor/pirate/str04aug
datasource = 'pirate'  # datasource within region
layer = 'str04aug'     # layer within datasource

cities_atof[None] = None

# States to insert into states table in insertStates()
states = [
    {'id': 'or', 'state': 'oregon'},
    {'id': 'wa', 'state': 'seattle'}
]

# dbf value => database value
one_ways = {
    'n': 0,
    'f': 1,
    't': 2,
    '':  3,
    None: 3
}

# dbf value => database value
bikemodes = {
    'mu': 't',
    'mm': 'p',
    'bl': 'b',
    'lt': 'l',
    'mt': 'm',
    'ht': 'h',
    'ca': 'c',
    'pm': 'x',
    'up': 'u',
    'pb': 'n',
    'xx': 'n',
    None: None,
}


### General Configuration
### Should apply to all regions
### May need to be changed depending on the local environment

# Path to shp-importing executable
shp2sql_exe = '/usr/bin/shp2pgsql'

# args template for shp-importing executable
shp2sql_args = '-c -i -I -s %s %s %s > %s' \
               # % (SRID, layer, schema, SQL file)

# Path to database executable
sql_exe = '/usr/bin/psql'

# args template for importing SQL into database
sql_args = '--quiet -d %s -f %s'  # % (database, SQL file)

# Base path to regional shapefiles
base_data_path = '/home/bycycle/byCycleData'

# Name of database
db_name = 'bycycle'


### Derived configuration
### Should also apply to all regions and should NOT be edited

# Path to region package and region package data files
region_path = os.path.join(install_path, 'model', region)
region_data_path = os.path.join(region_path, 'data')

# Path to regional shapefiles
data_path = os.path.join(base_data_path, region, datasource)

# Path to specific layer
layer_path = os.path.join(data_path, layer)

# Database config
db_schema = region
db_user = db_name
db_pw_path = os.path.join(install_path, region_data_path, '.pw')
db_pass = open(db_pw_path).read().strip()
# Raw tables go in the raw schema using the schema name as the table name.
# "This is the raw table for schema X." With the scheme, we can create and
# drop the "real" schema tables without worrying about the raw table.
raw_table = 'raw.%s' % db_schema

# Output file for SQL imported from shapefile
# Ex: ~/byCycle/evil/byCycle/model/portlandor/data/portlandor.str04aug.raw.sql
sql_file = '%s_%s_raw.sql' % (region, layer)
sql_file_path = os.path.join(region_data_path, sql_file)

# Complete command to convert shapefile to raw SQL
# Ex: /usr/lib/postgresql/8.1/bin/shp2pgsql -c -i -I -s 2913 \
#     str04aug raw.portlandor > /path/portlandor_str04aug_raw.sql
shp2sql_cmd = ' '.join((shp2sql_exe, shp2sql_args))
shp2sql_cmd = shp2sql_cmd % (srid, layer_path, raw_table, sql_file_path)

# Command to import raw SQL into database
# Ex: /usr/bin/psql --quiet -d bycycle -f /path/portlandor_str04aug_raw.sql
sql2db_cmd = ' '.join((sql_exe, sql_args))
sql2db_cmd = sql2db_cmd % (db_name, sql_file_path)


### Globals

# Underlying DBAPI database connection and cursor
connection = None
cursor = None

# Database engine
engine = None

# Metadata for schema tables
metadata = None

# Metadata for just the raw table
raw_metadata = None

# Schema tables (dict of {table name => table object})
tables = None

# Flat table the shapefile is imported into
raw_table = None

# All the rows in the raw table
raw_data = None

# Reused/reset for each action
timer = None

# Edge names {(prefix, name, type, suffix) => street name ID}
# Created in `transferStreetNames`
street_names = None

# Cities {full city name => city ID}
# Created in `transferCities`
cities = None


### Setup actions that always need to be done (or at least, they *can* always
### be done, because they don't have any destructive side effects)

def createConnection():
    """Set up and return DB connection."""
    return psycopg2.connect(host='localhost',
                            database=db_name,
                            user=db_user,
                            password=db_pass
                            )


def createDatabaseEngine(creator):
    engine = sqlalchemy.engine.create_engine('postgres://', creator=creator)
    return engine


def createMetadata(engine):
    metadata = sqlalchemy.schema.BoundMetaData(engine)
    metadata.engine.echo = True
    return metadata


def getTables(metadata, raw_metadata, schema):
    tables = Tables(schema, metadata, raw_metadata, add_geometry=False)
    raw_table = tables.raw_table
    return tables, raw_table


### Utilities used by the actions below

def system(cmd):
    """Run the command specified by ``cmd``."""
    print cmd
    exit_code = os.system(cmd)
    if exit_code:
        sys.exit()


def wait(msg='Continue or skip'):
    if no_prompt:
        return False
    timer.pause()
    resp = raw_input(msg + '? ')
    timer.unpause()
    return resp


def prompt(msg='', prefix=None, default='no'):
    """Prompt, wait for response, and return response.

    ``msg`` `string`
        The prompt message, in the form of a question.

    ``prefix``
        Something to prefix the prompt with (like a number to indicate which
        action we're on).

    ``default`` `string` `bool`
        The default response for this prompt (when the user just presses
        Enter). Can be 'n', 'no', or anything that will evaluate as False to
        set the default response to 'no'. Otherwise the default response will
        be 'yes'.

    Return `bool`
        True indicates a positive (Go ahead) response.
        False indicates a negative (Don't do it!) response.

    """
    msg = msg.strip() or 'Are you sure'
    # Prefix prompt with prefix if prefix supplied
    if prefix is None:
        p = ''
    else:
        p = '%s: ' % prefix
    # Determine if yes or no is the default response
    if not default or str(default).lower() in ('n', 'no'):
        choices = '[y/N]'
        default_is_yes = False
    else:
        choices = '[Y/n]'
        default_is_yes = True
    default_is_no = not default_is_yes
    # Print prompt and wait for response
    resp = raw_input('%s%s? %s '% (p, msg, choices)).strip().lower()
    # Interpret and return response
    if not resp:
        if default_is_yes:
            return True
        elif default_is_no:
            return False
    else:
        if resp[0] == 'y':
            return True
        elif resp[0] in ('q', 'x') or resp == 'exit':
            print '\n***Aborted at action %s.***' % prefix
            sys.exit(0)
        else:
            return False


def dropTable(table):
    # TODO: Try to make this work when the table has dependent tables
    try:
        # FIXME: checkfirst doesn't seem to work
        table.drop(checkfirst=True)
    except sqlalchemy.exceptions.SQLError, e:
        if not 'does not exist' in str(e):
            raise


def recreateTable(table):
    """Drop ``table`` from database and then create it."""
    dropTable(table)
    table.create()


def deleteAllFromTable(table):
    """Delete all records from ``table``."""
    table.delete().execute()


def turnSQLEchoOff(md):
    """Turn echoing of SQL statements off for ``md``."""
    md.engine.echo = False


def turnSQLEchoOn(md):
    """Turn echoing of SQL statements on for ``md``."""
    md.engine.echo = True


def vacuum(*tables):
    """Vacuum all tables."""
    print 'Vacuuming all tables...'
    connection.set_isolation_level(0)
    if not tables:
        cursor.execute('VACUUM FULL ANALYZE')
    else:
        for table in tables:
            cursor.execute('VACUUM FULL ANALYZE %s' % table)            
    connection.set_isolation_level(2)


def getEvenSide(addr_f_l, addr_f_r, addr_t_l, addr_t_r):
    """Figure out which side of the edge even addresses are on."""
    if ((addr_f_l and addr_f_l % 2 == 0) or
        (addr_t_l and addr_t_l % 2 == 0)):
        # Left?
        even_side = 'l'
    elif ((addr_f_r and addr_f_r % 2 == 0) or
          (addr_t_r and addr_t_r % 2 == 0)):
        # Right?
        even_side = 'r'
    else:
        # Couldn't tell.
        even_side = None
    return even_side


def getTimeWithUnits(seconds):
    """Convert ``seconds`` to minutes if >= 60. Return time with units."""
    if seconds >= 60:
        time = seconds / 60.0
        units = 'minute'
    else:
        time = seconds
        units = 'second'
    if time != 1.0:
        units +=  's'
    return '%.2f %s' % (time, units)


### Actions the user may or may not want to take

def shp2sql():
    """Convert shapefile to SQL and save to file."""
    system(shp2sql_cmd)


def shp2db():
    """Read shapefile into database table."""
    raw_table.drop(checkfirst=True)
    system(sql2db_cmd)
    vacuum('raw.%s' % region)


def dropTables():
    """Drop all schema tables (excluding raw)."""
    metadata.drop_all()


def createTables():
    """Create all tables. (Ignores existing tables.)"""
    Q = 'CREATE SCHEMA %s' % region
    try:
        cursor.execute(Q)
    except psycopg2.ProgrammingError:
        connection.rollback()  # important!
    else:
        connection.commit()
    metadata.create_all()
    # Add geometry columns after tables are created and add gist INDEXes them
    add_geom_col = """
    SELECT AddGeometryColumn('%s', '%s', 'geom', %s, '%s', 2)
    """
    create_gist_index = """
    CREATE INDEX "%s_the_geom_gist" 
    ON "%s"."%s" 
    USING GIST ("geom" gist_geometry_ops)
    """
    table_names = ('layer_edges', 'layer_nodes')
    geom_types = ('MULTILINESTRING', 'POINT')
    for table, geom_type in zip(table_names, geom_types):
        cursor.execute(add_geom_col % (db_schema, table, SRID, geom_type))
        cursor.execute(create_gist_index % (table, db_schema, table))
    connection.commit()
    # The above added cols to the DB; this adds them to SQLAlchemy table defs
    tables._appendGeometryColumns()


def transferStreetNames(modify=True):
    """Transfer street names from raw table to schema table.

    This also has the side effect of setting the global `street_names`, which
    is a dict of {(prefix, name, type, suffix) => street name ID} that
    gets used in `transferStreets`.

    ``modify`` `bool`
        If this is set the street names table won't be modified in any way
        (i.e., rows won't be deleted and inserted), but the global
        `street_names` will still be created.

    TODO: Convert all street types to USPS standard

    """
    global street_names
    street_names = {}
    table = tables.street_names
    # Get all distinct street names from raw (in lowercase)
    cols = (raw_table.c.fdpre, raw_table.c.fname, raw_table.c.ftype,
            raw_table.c.fdsuf)
    sel_cols = map(sqlalchemy.sql.func.lower, cols)
    result = sqlalchemy.sql.select(sel_cols, distinct=True).execute()
    # Transfer street names, creating sequential IDs for them
    l = []
    street_name_id = 1
    for row in result:
        p, n, s, t = row[0], row[1], row[2], row[3]
        if (p or n or s or t or None) is not None:
            street_names[(p, n, s, t)] = street_name_id
            d = {}
            d['id'] = street_name_id
            d['prefix'] = p
            d['name'] = n or '[No Name]'
            d['sttype'] = s
            d['suffix'] = t
            l.append(d)
            street_name_id += 1
    street_names[(None, None, None, None)] = None
    result.close()
    # Delete all the old street names and insert the new ones
    if modify:
        deleteAllFromTable(table)
        turnSQLEchoOff(metadata)
        table.insert().execute(l)
        turnSQLEchoOn(metadata)


def transferCities(modify=True):
    """Transfer cities from raw table to schema cities table.

    The city names are abbreviated in the raw table; they are looked up and
    converted to their (lowercase) full names after being transferred.

    This also has the side effect of setting the global `cities`, which is a
    dict of {full city name => city ID} that gets used in `transferStreets`.

    ``modify`` `bool`
        If this is set the cities table won't be modified in any way (i.e.,
        rows won't be deleted and inserted), but the global `cities` will
        still be created.

    """
    global cities
    cities = {}
    table = tables.cities
    # Get distinct cities from raw (in lowercase)
    for col in (raw_table.c.lcity, raw_table.c.rcity):
        col = sqlalchemy.sql.func.lower(col)
        sel = sqlalchemy.sql.select([col], col != None, distinct=True)
        result = sel.execute()
        for row in result:
            city = row[0]
            cities[cities_atof[city]] = 1
        result.close()
    # Transfer cities, creating sequential IDs for them
    l = []
    city_names = cities.keys()
    city_names.sort()
    city_id = 1
    for city in city_names:
        if city is not None:
            cities[city] = city_id
            d = {}
            d['id'] = city_id
            d['city'] = city
            l.append(d)
            city_id += 1
    cities[None] = None
    # Delete all the old cities and insert the new ones
    if modify:
        deleteAllFromTable(table)
        turnSQLEchoOff(metadata)
        table.insert().execute(l)
        turnSQLEchoOn(metadata)


def insertStates():
    table = tables.states
    deleteAllFromTable(table)
    table.insert().execute(states)


def transferNodeIDs(modify=True):
    """Transfer node IDs from raw table to node table."""
    table = tables.layer_nodes
    c = raw_table.c
    nodes = {}
    # Get distinct node IDs from raw table
    for node_id in (c.fnode, c.tnode):
        cols = [node_id.label('node_id')]
        result = select(cols, distinct=True).execute()
        for row in result:
            nodes[row.node_id] = 1
        result.close()
    l = []
    for node_id in nodes:
        # Collect all the row data so all the rows can be inserted at once
        d = {}
        d['id'] = node_id
        #d['geom'] = None
        l.append(d)
    if modify:
        # Drop existing nodes and add all new nodes at once
        deleteAllFromTable(table)
        turnSQLEchoOff(metadata)
        table.insert().execute(l)
        turnSQLEchoOn(metadata)


def transferEdges(modify=True):
    """Transfer edge geometry and attributes to streets table."""
    tables._appendGeometryColumns()
    table = tables.layer_edges
    if street_names is None:
        print 'Getting street names...'
        transferStreetNames(modify=False)
    if cities is None:
        print 'Getting cities...'
        transferCities(modify=False)
    # Get selected columns for all rows in raw
    c = raw_table.c
    func_lower = sqlalchemy.sql.func.lower
    cols = [
        # Core attributes
        c.gid,
        c.the_geom, c.fnode, c.tnode,

        # Core address attributes
        c.leftadd1, c.leftadd2, c.rgtadd1, c.rgtadd2,
        func_lower(c.fdpre).label('prefix'),
        func_lower(c.fname).label('name'),
        func_lower(c.ftype).label('sttype'),
        func_lower(c.fdsuf).label('suffix'),
        func_lower(c.lcity).label('city_l'),
        func_lower(c.rcity).label('city_r'),
        c.zipcolef, c.zipcorgt,

        # Additional attributes
        func_lower(c.one_way).label('one_way'),
        c.localid, c.type,
        func_lower(c.bikemode).label('bikemode'),
        c.up_frac, c.abs_slp, c.sscode, c.cpd
    ]
    result = select(cols).execute()
    # Transfer streets
    l = []
    for i, row in enumerate(result):
        addr_f_l, addr_f_r = row.leftadd1, row.rgtadd1
        addr_t_l, addr_t_r = row.leftadd2, row.rgtadd2
        # Unify "from" addresses
        if addr_f_l is not None or addr_f_r is not None:
            addr_f = int(round((addr_f_l or addr_f_r) / 10.0) * 10) + 1
        else:
            addr_f = None
        # Unify "to" addresses
        if addr_t_l is not None or addr_t_r is not None:
            addr_t = int(round((addr_t_l or addr_t_r) / 10.0) * 10)
        else:
            addr_t = None
        # Street name: prefix, name, type, suffix
        street_name_parts = (
            row.prefix, row.name, row.sttype, row.suffix
        )
        lcity = row.city_l
        rcity = row.city_r
        one_way = row.one_way
        bikemode = row.bikemode
        d = {}
        d['id'] = row.gid
        d['geom'] = row.the_geom
        d['node_f_id'] = row.fnode
        d['node_t_id'] = row.tnode
        d['addr_f'] = addr_f
        d['addr_t'] = addr_t
        d['even_side'] = getEvenSide(addr_f_l, addr_f_r, addr_t_l, addr_t_r)
        d['street_name_id'] = street_names[street_name_parts]
        d['city_l_id'] = cities[cities_atof[lcity]]
        d['city_r_id'] = cities[cities_atof[rcity]]
        d['state_l_id'] = ['or', 'wa'][lcity == 'van']
        d['state_r_id'] = ['or', 'wa'][rcity == 'van']
        d['zip_code_l'] = row.zipcolef
        d['zip_code_r'] = row.zipcorgt
        d['localid'] = row.localid
        d['one_way'] = one_ways[one_way]
        d['bikemode'] = bikemodes[bikemode]
        d['code'] = row.type
        d['up_frac'] = row.up_frac
        d['abs_slp'] = row.abs_slp
        d['cpd'] = row.cpd
        d['sscode'] = row.sscode
        l.append(d)
    result.close()
    if modify:
        deleteAllFromTable(table)
        turnSQLEchoOff(metadata)
        table.insert().execute(l)
        turnSQLEchoOn(metadata)
        vacuum('%s.layer_edges' % region)


def convertEdgeGeometryToLINESTRING():
    """Convert edge geometry from MULTILINESTRING to LINESTRING."""
    Qs = (
        # Drop the MULTILINESTRING constraint.
        """
        ALTER TABLE
        %s.layer_edges
        DROP CONSTRAINT
        enforce_geotype_geom
        """ % db_schema,

        # Update geometries, converting MULTILINESTRING to LINESTRING.
        # TODO: Check for MULTILINESTRINGs with more than one LINESTRING and
        # try to merge those LINESTRINGs together.
        """
        UPDATE
        %s.layer_edges
        SET geom = GeometryN(geom, 1)
        """ % db_schema,

        # Add a LINESTRING constraint to the geometry column.
        """
        ALTER TABLE
        %s.layer_edges
        ADD CONSTRAINT
        enforce_geotype_geom
        CHECK
        ((geometrytype(geom) = 'LINESTRING'::text OR geom IS NULL))
        """ % db_schema
    )
    for Q in Qs:
        cursor.execute(Q)
    connection.commit()


def transferNodeGeometry(modify=True):
    """Copy node geometry from edge table to node table."""
    tables._appendGeometryColumns()
    table = tables.layer_nodes
    layer_edges = tables.layer_edges
    c = layer_edges.c
    nodes = {}
    # Get distinct node IDs from raw table
    cols = [c.node_f_id, c.node_t_id, c.geom]
    result = select(cols).execute()
    for row in result:
        line = row.geom
        nodes[row.node_f_id] = line.startPoint()
        nodes[row.node_t_id] = line.endPoint()
    result.close()
    l = []
    for node_id in nodes:
        # Collect all the row data so all the rows can be updated at once
        d = {}
        d['id'] = node_id
        d['geom'] = nodes[node_id]
        l.append(d)
    if modify:
        # Transfer node geometries
        turnSQLEchoOff(metadata)
        table.update(table.c.id==bindparam('id')).execute(l)
        turnSQLEchoOn(metadata)


### Actions list, in the order they will be run

actions = (
    # 0
    (shp2sql,
     'Convert shapefile to raw SQL and save to file',
     'Converted shapefile to SQL and saved SQL to %s.' % sql_file_path,
     ),

    # 1
    (shp2db,
     'Drop existing raw table and insert raw SQL into database',
     'Dropped existing raw table and inserted raw SQL from %s into %s.' % \
     (sql_file_path, raw_table),
     ),

    # 2
    (dropTables,
     'Drop schema tables (not including raw table)',
     'Dropped schema tables, except raw.',
     ),

    # 3
    (createTables,
     'Create schema tables (ignoring existing tables)',
     'Created schema tables that didn\'t already exist.',
     ),

    # 4
    (transferStreetNames,
     'Transfer street names from raw table',
     'Transferred street names from raw table to street name table',
    ),

    # 5
    (transferCities,
     'Transfer cities from raw table',
     'Transferred cities from raw table to city table',
     ),

    # 6
    (insertStates,
     'Insert states',
     'States inserted into state table'
     ),

    # 7
    (transferNodeIDs,
     'Transfer node IDs from raw table',
     'Transferred node IDs from raw table to node table'
     ),

    # 8
    (transferEdges,
     'Transfer edges from raw table',
     'Transferred edge geometry and attributes from raw table to edge '
     'table',
     ),

    # 9
    (convertEdgeGeometryToLINESTRING,
     'Convert edge table geometry from MULTILINESTRING to LINESTRING',
     'Converted edge table geometry to LINESTRING and'
     'added LINESTRING check constraint',
     ),

    # 10
    (transferNodeGeometry,
     'Transfer node geometry from edge table',
     'Transferred node geometry from edge table to node table',
     ),
)


def doActions(actions, start, end, no_prompt):
    do_prompt = not no_prompt
    overall_timer = meter.Timer()
    overall_timer.start()
    print
    for i, action in enumerate(actions):
        func = action[0]
        before_msg = action[1]
        after_msg = action[2]
        try:
            default_response = action[3]
        except IndexError:
            default_response = False
        if i < start or i > end:
            print '%s: Skipping "%s."' % (i, before_msg)
        else:
            if do_prompt:
                # Ask user, "Do you want do this action?"
                overall_timer.pause()
                response = prompt(msg=before_msg, prefix=i,
                                  default=default_response)
                overall_timer.unpause()
            else:
                print '%s...' % before_msg
            if no_prompt or response:
                # Yes, do this action
                timer.start()
                try:
                    apply(func)
                except Exception, e:
                    print '\n*** Errors encountered in action %s. ' \
                          'See log. ***' % i
                    raise
                print after_msg, '\nTook %s.' % getTimeWithUnits(timer.stop())
            else:
                # No, don't do this action
                print 'Skipped'
        print
    vacuum()
    print 'Total time: %s' % getTimeWithUnits(overall_timer.stop())

### Event loop (so to speak)

def run(start=0, end=len(actions)-1, no_prompt=False, only=None):
    if only is not None:
        start = only
        end = only
        no_prompt = True
    doActions(actions, start, end, no_prompt)


def main(argv):
    args_dict = getOpts(sys.argv[1:])
    # Set up globals
    global connection, cursor, engine, metadata, tables, raw_table, raw, timer
    engine = createDatabaseEngine(createConnection)
    connection = engine.raw_connection()
    cursor = connection.cursor()
    metadata = createMetadata(engine)
    raw_metadata = createMetadata(engine)
    tables, raw_table = getTables(metadata, raw_metadata, db_schema)
    # raw_data = ...
    timer = meter.Timer(start_now=False)
    # Enter event loop
    sys.stderr = open('shp2pgsql.error.log', 'w')
    run(**args_dict)


def getOpts(argv):
    args_dict = {
        'start': 0,
        'end': len(actions) - 1,
        'no_prompt': False,
        'only': None,
        }
    # Parse args
    try:
        short_opts = 's:e:no:h'
        long_opts = ['start=', 'end=', 'no-prompt', 'only=', 'help']
        opts, args = getopt.gnu_getopt(argv, short_opts, long_opts)
    except getopt.GetoptError, e:
        error(2, str(e))
    start_or_end_specified = False
    # See what args were given and put them in the args dict
    for opt, val in opts:
        if opt not in ('--no-prompt', '-n', '--help', '-h'):
            try:
                val = int(val)
            except ValueError:
                error(2, 'All option values must be integers.')
        if opt in ('--start', '-s'):
            start_or_end_specified = True
            args_dict['start'] = val
        elif opt in ('--end', '-e'):
            start_or_end_specified = True
            args_dict['end'] = val
        elif opt in ('--no-prompt', '-n'):
            args_dict['no_prompt'] = True
        elif opt in ('--only', '-o'):
            args_dict['only'] = val
        elif opt in ('--help', '-h'):
            usage()
            sys.exit()
    if args_dict['only'] is not None:
        if start_or_end_specified:
            error(2, '`only` must be the *only* argument or not specified.')
        else:
            args_dict['no_prompt'] = True
    return args_dict


def error(code, msg):
    usage(msg='Error: %s' % msg)
    sys.exit(code)


def usage(msg=''):
    if msg:
        print '\n%s' % msg
    print __doc__


if __name__ == '__main__':
    main(sys.argv)
