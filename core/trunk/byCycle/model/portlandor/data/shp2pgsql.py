#!/usr/bin/env python2.5
################################################################################
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
################################################################################
"""
Usage: shp2pgsql.py [various options]

There are three forms for running this script. All version require that the
datasource and layer be specified. In the following, replace "shp2pgsql.py"
with::

  shp2pgsql.py --source <path to datasource> --layer <layer within datasource>

1. This will run through all the actions, prompting you for each one:

  shp2pgsql.py

2. This will either prompt you to run the actions from indices i to j in the
  actions list or just run all the actions from i to j if `no-prompt` is
  specified:

  shp2pgsql.py [--start|-s <i>] [--end|-e <j>] [--no-prompt|-n]

3. This will run only the action at index i without prompting:

  shp2pgsql.py --only|-o <i>

Defaults:
    - start=0
    - end=n-1 where n is the number of actions
    - no-prompt flag off
    - only not used

If no args are supplied, you will be prompted to run all actions.

If either of ``start`` or ``end`` (or both) is present, the ``only`` option
must not be present.

If ``only`` is present, ``no-prompt`` is implied.

"""
import os
import sys
import getopt

import psycopg2
import psycopg2.extensions

import sqlalchemy
from sqlalchemy.sql import func, select, bindparam
from sqlalchemy.sql import and_, or_
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer

from cartography import geometry

from byCycle.model.data.sqltypes import Geometry

from byCycle.util import meter
from byCycle import model
from byCycle.model import db

from byCycle.model.sttypes import street_types_ftoa
from byCycle.model import Region, EdgeAttr
from byCycle.model.portlandor import Node, Edge, StreetName, City, State, Place
from byCycle.model.portlandor.data import (title, slug, SRID, units,
                                           edge_attrs, earth_circumference,
                                           block_length, jog_length,
                                           Raw)
from byCycle.model.portlandor.data.cities import cities_atof


### Region Configuration
### Should be the only configuration that gets changed per-region

# Target format: /base/path/to/regional_data/specific_region/datasource/layer
# Ex: /home/bycycle/byCycle/data/portlandor/pirate/str04aug
#datasource = 'pirate'  # datasource within region
#layer = 'str06oct'     # layer within datasource

cities_atof[None] = None

# States to insert into states table in insert_states()
states = {'or': 'oregon', 'wa': 'washington'}

# dbf value => database value
one_ways = {'n': 0, 'f': 1, 't': 2, '':  3, None: 3}

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
shp2sql_exe = 'shp2pgsql'

# args template for shp-importing executable
shp2sql_args = '-c -i -I -s %s %s %s.%s > %s' \
               # % (SRID, layer, schema, SQL file)

# Path to database executable
sql_exe = 'psql'

# args template for importing SQL into database
sql_args = '--quiet -d %s -f %s'  # % (database, SQL file)

## TODO: convert these two to command line arg with these values as defaults
# Base path to regional shapefiles
base_data_path = os.path.join(os.environ['HOME'], 'byCycleData')
# Name of database
db_name = 'bycycle'


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
    resp = raw_input(msg.strip() + ' ')
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


def any_not_none(sequence):
    """Return ``True`` if any item in ``sequence`` is not ``None``."""
    return any([e is not None for e in sequence])


def delete_edges():
    col = Edge.c['%s_edge_id' % slug]
    map(Edge.delete, Edge.select(col != None))
    db.flush()
    #db.deleteAllFromTable(RegionEdge.table)


def delete_nodes():
    col = Node.c['%s_node_id' % slug]
    map(Node.delete, Node.select(col != None))
    db.flush()
    #db.deleteAllFromTable(RegionNode.table)


def get_records(cols, distinct=True):
    """Get distinct records.

    ``cols``
        The list of cols to select

    return
        A ``set`` of ``tuple``s of column values, in the same order as
        ``cols``

    """
    result = select(cols, distinct=distinct).execute()
    records = set([tuple([v for v in row])
                   for row in result
                   if any_not_none(row)])
    result.close()
    return records


def insert_records(table, records, kind='records'):
    """Insert ``records`` into ``table``.

    ``table``
        SQLAlchemy table object

    ``records``
        A ``list`` of ``dict``s representing the records

    """
    if records:
        table.insert().execute(records)
        echo('%i new %s added' % (len(records), kind))
    else:
        echo('No new %s added' % kind)


def get_sql_file_path():
    """Get output file for SQL imported from shapefile.

    The output file will be created in the directory this script is in. It
    will include the region's schema (AKA slug), datasource, and layer::

        /path/to/here/<slug>_<source>_<layer>_raw.sql

    """
    sql_file = '%s_%s_%s_raw.sql' % (slug, source.replace('/', '_'), layer)
    sql_file_path = os.path.join(os.path.dirname(__file__), sql_file)
    return sql_file_path


def vacuum_entity(entity):
    args = (entity.table.schema, entity.table.name)
    echo('Vacuuming %s.%s...' % args)
    db.vacuum('%s.%s' % args)


### Actions the user may or may not want to take

def shp2sql():
    """Convert shapefile to SQL and save to file."""
    # Path to regional shapefiles
    data_path = os.path.join(base_data_path, slug, source)

    # Path to specific layer
    layer_path = os.path.join(data_path, layer)

    # Command to convert shapefile to raw SQL
    # Ex: shp2pgsql -c -i -I -s 2913 str06oct raw.portlandor > \
    #         /path/portlandor_str06oct_raw.sql
    shp2sql_cmd = ' '.join((shp2sql_exe, shp2sql_args))
    shp2sql_cmd = shp2sql_cmd % (SRID, layer_path, Raw.table.schema,
                                 Raw.table.name, get_sql_file_path())
    system(shp2sql_cmd)


def shp2db():
    """Read shapefile into database table (raw.``slug``)."""
    # Command to import raw SQL into database
    # Ex: psql --quiet -d bycycle -f /path/portlandor_str04aug_raw.sql
    sql2db_cmd = ' '.join((sql_exe, sql_args))
    sql2db_cmd = sql2db_cmd % (db_name, get_sql_file_path())
    Q = 'CREATE SCHEMA raw'
    try:
        db.execute(Q)
    except psycopg2.ProgrammingError:
        db.rollback()  # important!
    else:
        db.commit()
    db.dropTable(Raw.table)
    system(sql2db_cmd)
    db.vacuum('raw.%s' % slug)


def delete_region():
    """Delete all regional records from database.

    Deleting records in the "top most" tables (edge, node) should cascade and
    delete all child records in other tables.

    """
    Q = "DELETE FROM region WHERE slug = '%s'" % slug
    echo(Q)
    db.execute(Q)
    db.commit()


def get_or_create_region():
    Region.table.create(checkfirst=True)
    try:
        region = Region.get_by(slug=slug)
    except sqlalchemy.exceptions.SQLError, e:
        echo(e)
        region = None
    if region is None:
        record = dict(
            title=title,
            slug=slug,
            srid=SRID,
            units=units,
            earth_circumference=earth_circumference,
            block_length=block_length,
            jog_length=jog_length,
        )
        insert_records(Region.table, [record], 'region')
        region = Region.get_by(slug=slug)
        region.edge_attrs = []
        region.flush()
        attrs = [dict(name=a, region_id=region.id) for a in edge_attrs]
        insert_records(EdgeAttr.table, attrs, 'edge attributes')
    return region


def drop_tables():
    """Drop all regional tables (not including raw)."""
    region = get_or_create_region()
    md = region.module.metadata
    for t in md.table_iterator():
        db.dropTable(t, cascade=True)


def create_tables():
    """Create all regional tables. Ignores existing tables."""
    region = get_or_create_region()
    region.module.metadata.create_all()
    schema = Edge.table.schema
    db.addGeometryColumn(Edge.table.name, SRID, 'LINESTRING', schema=schema)
    db.addGeometryColumn(Node.table.name, SRID, 'POINT', schema=schema)


def transfer_street_names():
    region = get_or_create_region()
    region_id = region.id
    c = Raw.c
    cols = map(func.lower, (c.prefix, c.name, c.sttype, c.suffix))
    raw_records = get_records(cols)
    c = StreetName.c
    cols = map(func.lower, (c.prefix, c.name, c.sttype, c.suffix))
    existing_records = get_records(cols)
    new_records = raw_records.difference(existing_records)
    records = []
    for record in new_records:
        p, n, t, s = record
        t = street_types_ftoa.get(t, t)
        records.append(dict(prefix=p, name=n, sttype=t, suffix=s))
    echo('Inserting street names...')
    insert_records(StreetName.table, records, 'street names')
    vacuum_entity(StreetName)


def transfer_cities():
    c = Raw.c
    raw_records_l = get_records([func.lower(c.city_l)])
    raw_records_r = get_records([func.lower(c.city_r)])
    raw_records = raw_records_l.union(raw_records_r)
    raw_records = set([(cities_atof[r[0]],) for r in raw_records])
    existing_records = get_records([City.c.city])
    new_records = raw_records.difference(existing_records)
    records = []
    city_names = []
    for r in new_records:
        city_name = r[0]
        city_names.append(city_name)
        records.append(dict(city=city_name))
    insert_records(City.table, records, 'cities')
    vacuum_entity(City)


def insert_states():
    raw_records = set(states.items())
    existing_records = get_records([State.c.code, State.c.state])
    new_records = raw_records.difference(existing_records)
    records = []
    codes = []
    for r in new_records:
        code, state = r[0], r[1]
        codes.append(code)
        records.append(dict(code=code, state=state))
    insert_records(State.table, records, 'states')
    vacuum_entity(State)


def transfer_places():
    c = Raw.c
    cols = (func.lower(c.city_l), c.zip_code_l)
    raw_records_l = get_records(cols)
    cols = (func.lower(c.city_r), c.zip_code_r)
    raw_records_r = get_records(cols)
    raw_records = raw_records_l.union(raw_records_r)
    def get_city_state_and_zip(r):
        city = cities_atof[r[0]]
        state = 'or' if city != 'vancouver' else 'wa'
        return city, state, r[1]
    raw_records = set([get_city_state_and_zip(r) for r in raw_records])
    places = Place.select()
    existing_records = set([(None if p.city is None else p.city.city,
                             None if p.state is None else p.state.code,
                             p.zip_code)
                            for p in places])
    new_records = raw_records.difference(existing_records)
    records = []
    for r in new_records:
        city_name, state_code, zc = r[0], r[1], r[2]
        city = City.get_by(city=city_name)
        state = State.get_by(code=state_code, state=states[state_code])
        city_id = None if city is None else city.id
        state_id = None if state is None else state.id
        records.append(dict(city_id=city_id, state_id=state_id, zip_code=zc))
    insert_records(Place.table, records, 'places')
    vacuum_entity(Place)


def transfer_nodes():
    """Transfer nodes from raw table to node table."""
    region = get_or_create_region()

    echo('Getting columns from raw table...')
    c = Raw.c
    raw_records_f = get_records([c.node_f_id, func.startPoint(c.geom)],
                                distinct=False)
    raw_records_t = get_records([c.node_t_id, func.endPoint(c.geom)],
                                distinct=False)

    records = []
    seen_nodes = {}
    def collect_records(raw_records):
        for r in raw_records:
            node_id = r[0]
            if node_id in seen_nodes:
                continue
            seen_nodes[node_id] = 1
            geom = r[1]
            records.append(dict(id=node_id, geom=geom))
    collect_records(raw_records_f)
    collect_records(raw_records_t)

    echo('Inserting records into node table...')
    insert_records(Node.table, records, 'nodes')

    vacuum_entity(Node)


def transfer_edges():
    """Transfer edge geometry and attributes to streets table."""
    region = get_or_create_region()

    echo('Getting columns from raw table...')
    c = Raw.c
    cols = [
        c.id, c.geom, c.node_f_id, c.node_t_id,
        c.addr_f_l, c.addr_t_l, c.addr_f_r, c.addr_t_r,
        c.zip_code_l, c.zip_code_r,
        c.localid, c.code, c.up_frac, c.abs_slope, c.sscode, c.cpd
    ]
    lower_cols = [
        c.prefix, c.name, c.sttype, c.suffix,
        c.city_l, c.city_r, c.one_way, c.bikemode
    ]
    for i, col in enumerate(lower_cols):
        lower_cols[i] = func.lower(col).label(col.key)
    cols += lower_cols
    raw_records = select(cols).execute()

    echo('Getting street names...')
    c = StreetName.c
    street_names = get_records((c.prefix, c.name, c.sttype, c.suffix, c.id))
    street_names = dict([((r[0], r[1], r[2], r[3]), r[4]) for r in
                         street_names])
    street_names[(None, None, None, None)] = None

    echo('Getting places...')
    places = Place.select()
    places = dict([((None if p.city is None else p.city.city,
                     None if p.state is None else p.state.code,
                     p.zip_code),p.id)
                     for p in places])
    places[(None, None, None)] = None

    echo('Transferring edges...')
    i = 1
    step = 2500
    num_records = raw_records.rowcount
    records = []
    for r in raw_records:
        even_side = getEvenSide(r.addr_f_l, r.addr_f_r, r.addr_t_l, r.addr_t_r)
        sttype = street_types_ftoa.get(r.sttype, r.sttype)
        st_name_id = street_names[(r.prefix, r.name, sttype, r.suffix)]
        city_l = cities_atof[r.city_l]
        city_r = cities_atof[r.city_r]
        state_l = 'or' if city_l != 'vancouver' else 'wa'
        state_r = 'or' if city_r != 'vancouver' else 'wa'
        place_l_id = places[(city_l, state_l, r.zip_code_l)]
        place_r_id = places[(city_r, state_r, r.zip_code_r)]
        records.append(dict(
            addr_f_l=r.addr_f_l or None,
            addr_f_r=r.addr_f_r or None,
            addr_t_l=r.addr_t_l or None,
            addr_t_r=r.addr_t_r or None,
            even_side=even_side,
            one_way=one_ways[r.one_way],
            node_f_id=r.node_f_id,
            node_t_id=r.node_t_id,
            street_name_id=st_name_id,
            place_l_id=place_l_id,
            place_r_id=place_r_id,
            # region-specific fields:
            geom=r.geom.geometryN(0),
            localid=r.localid,
            bikemode=bikemodes[r.bikemode],
            code=r.code,
            up_frac=r.up_frac,
            abs_slope=r.abs_slope,
            cpd=r.cpd,
            sscode=r.sscode
        ))
        if (i % step) == 0:
            echo('Inserting %s records into edge table...' % step)
            insert_records(Edge.table, records, 'edges')
            echo('%i down, %i to go' % (i, num_records - i))
            records = []
        i += 1
    if records:
        echo('Inserting remaining records into edge table...')
        insert_records(Edge.table, records, 'edges')
    vacuum_entity(Edge)


def associate_edges_with_nodes():
    table_name = 'node_edges__edge'
    table = db.metadata.tables[table_name]
    region = get_or_create_region()
    echo('Removing existing associations...')
    db.execute('DELETE FROM %s WHERE node_id IN '
               '(SELECT id FROM node WHERE region_id = %i)' %
               (table_name, region.id))
    db.commit()
    echo('Getting Edge records...')
    c = Edge.c
    edges_f = get_records([c.id, c.node_f_id])
    edges_t = get_records([c.id, c.node_t_id])
    edges = edges_f.union(edges_t)
    records = [(dict(edge_id=e[0], node_id=e[1])) for e in edges]
    def _insert(records):
        echo('Inserting %i records...' % len(records))
        insert_records(table, records, '"nodes => edges"')
    while len(records) > 1000:
        _insert(records[:1000])
        records = records[1000:]
    if records:
        _insert(records)


### Actions list, in the order they will be run

def init_actions():
    global actions
    sql_file_path = get_sql_file_path()
    actions = (
        # 0
        (shp2sql,
         'Convert shapefile to raw SQL and save to file',
         'Converted shapefile to SQL and saved SQL to %s.' % sql_file_path,
         ),

        # 1
        (shp2db,
         'Drop existing raw table and insert raw SQL into database',
         'Dropped existing raw table\nInserted raw SQL from %s into %s' %
         (sql_file_path, Raw.table.name),
         ),

        # 2
        (delete_region,
         'Delete region "%s" (including all dependent records!)' % slug,
         'Deleted region "%s"' % slug,
         ),

        # 3
        (get_or_create_region,
         'Create region "%s"' % slug,
         'Created region "%s"' % slug,
         ),

        # 4
        (drop_tables,
         'Drop schema tables (not including raw table)',
         'Dropped schema tables, except raw.',
         ),

        # 5
        (create_tables,
         'Create ALL tables (ignoring existing tables)',
         'Created all tables that didn\'t already exist.',
         ),

        # 6
        (transfer_street_names,
         'Transfer street names from raw table',
         'Transferred street names from raw table to street name table',
        ),

        # 7
        (transfer_cities,
         'Transfer cities from raw table',
         'Transferred cities from raw table to city table',
        ),

        # 8
        (insert_states,
         'Insert states',
         'Inserted states'
         ),

        # 9
        (transfer_places,
         'Create places',
         'Places created',
         ),

        # 10
        (transfer_nodes,
         'Transfer nodes from raw table',
         'Transferred node IDs from raw table to node table'
         ),

        # 11
        (transfer_edges,
         'Transfer edges from raw table',
         'Transferred edge geometry and attributes from raw table to edge '
         'table',
         ),
    )

def run(start=0, end=None, no_prompt=False, only=None):
    if only is not None:
        start = only
        end = only
        no_prompt = True
    do_prompt = not no_prompt
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
                print '%s: %s...' % (i, before_msg)
            if no_prompt or response:
                # Yes, do this action
                timer.start()
                try:
                    apply(func)
                except Exception, e:
                    print ('\n*** Errors encountered in action %s. '
                           'See log. ***' % i)
                    raise
                msgs = after_msg.strip().split('\n')
                for m in msgs:
                    print m
                print 'Took %s' % getTimeWithUnits(timer.stop())
            else:
                # No, don't do this action
                print 'Skipped'
        print
    #db.vacuum()

def main(argv):
    global overall_timer, timer, source, layer, no_prompt
    overall_timer = meter.Timer()
    overall_timer.start()
    timer = meter.Timer(start_now=False)
    args_dict = getOpts(sys.argv[1:])
    source = args_dict.get('source')
    layer = args_dict.get('layer')
    no_prompt = bool(args_dict.get('no_prompt', args_dict.get('only', False)))
    sys.stderr = open('shp2pgsql.error.log', 'w')
    init_actions()
    if args_dict['end'] is None:
        args_dict['end'] = len(actions) - 1
    args_dict.pop('source')
    args_dict.pop('layer')
    run(**args_dict)
    print 'Total time: %s' % getTimeWithUnits(overall_timer.stop())

def getOpts(argv):
    args_dict = {
        'source': None,
        'layer': None,
        'start': 0,
        'end': None,
        'no_prompt': False,
        'only': None,
        }
    # Parse args
    try:
        short_opts = 'd:l:s:e:no:h'
        long_opts = ['source=', 'layer=', 'start=', 'end=', 'no-prompt',
                     'only=', 'help']
        opts, args = getopt.gnu_getopt(argv, short_opts, long_opts)
    except getopt.GetoptError, e:
        usage()
        die(2, str(e))
    start_or_end_specified = False
    # See what args were given and put them in the args dict
    for opt, val in opts:
        if opt not in ('--source', '--layer', '--no-prompt', '-n', '--help',
                       '-h'):
            try:
                val = int(val)
            except ValueError:
                die(2, '%s value must be an integer.' % opt)
        if opt in ('--source', '-d'):
            args_dict['source'] = val
        elif opt in ('--layer', '-l'):
            args_dict['layer'] = val
        elif opt in ('--start', '-s'):
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
        else:
            usage()
            die(1, 'Unknown option: ``%s``' % opt)
    if args_dict['only'] is not None:
        if start_or_end_specified:
            usage()
            die(2, '`only` must be the *only* argument or not specified.')
        else:
            args_dict['no_prompt'] = True
    return args_dict

def echo(*args):
    for msg in args:
        print '    - %s' % msg

def die(code=1, msg=''):
    print 'ERROR: %s' % msg
    print '(shp2pgsql.error.log may contain details.)'
    sys.exit(code)

def usage(msg=''):
    if msg:
        print '\n%s' % msg
    print __doc__


if __name__ == '__main__':
    main(sys.argv)
