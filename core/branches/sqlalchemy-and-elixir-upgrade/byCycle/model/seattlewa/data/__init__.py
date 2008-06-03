###############################################################################
# $Id: __init__.py 497 2007-02-18 02:04:51Z bycycle $
# Created 2007-05-31
#
# Seattle, WA, data
#
# Copyright (C) 2006 Wyatt Baldwin, byCycle.org <wyatt@bycycle.org>.
# All rights reserved.
#
# For terms of use and warranty details, please see the LICENSE file included
# in the top level of this distribution. This software is provided AS IS with
# NO WARRANTY OF ANY KIND.
###############################################################################
"""This package contains everything to do with this region's data and DB."""
from elixir import Entity, using_options, using_table_options
from elixir import has_field
from elixir import Integer, String, Integer, Float, Numeric

from byCycle.model import db
from byCycle.model.data.sqltypes import MULTILINESTRING

__all__ = ['title', 'slug', 'SRID', 'units', 'earth_circumference',
           'block_length', 'jog_length', 'cities_atof', 'states', 'one_ways',
           'bikemodes', 'edge_attrs', 'Raw']


title = 'City of Seattle'
slug = 'seattlewa'
SRID = 2285
units = 'feet'
earth_circumference = 131484672
block_length = 260
jog_length = block_length / 2
edge_attrs = []

cities_atof = {
    '0': 'seattle',
    '1': 'seattle',
    None: None,
}

# States to insert into states table in insert_states()
states = {'wa': 'washington', None: None}

# dbf value => database value
one_ways = {'0': 0, '1': 1, '2': 2, '3':  3, '': 3, None: 3}

# dbf value => database value
bikemodes = {
    '0': 0,
    '1': 1,
    '2': 2,
    '3': 3,
    '4': 4,
    None: None,
}

metadata = db.metadata_factory(slug)


class Raw(Entity):
    using_options(tablename=slug)
    using_table_options(schema='raw')

    has_field('gid', Integer, primary_key=True, key='id')

    # To edge table (core)
    has_field('the_geom', MULTILINESTRING(SRID), key='geom')
    has_field('fnode_', Integer, key='node_f_id')
    has_field('tnode_', Integer, key='node_t_id')
    has_field('l_add_from', Integer, key='addr_f_l')
    has_field('l_add_to', Integer, key='addr_t_l')
    has_field('r_add_from', Integer, key='addr_f_r')
    has_field('r_add_to', Integer, key='addr_t_r')
    has_field('snd_id', Integer, key='permanent_id')
    has_field('st_code', Integer, key='code')
    has_field('one_way', Integer)
    has_field('bikeclass', String(2), key='bikemode')

    # To street names table
    has_field('pre_dir', String(2), key='prefix')
    has_field('street_nam', String(30), key='name')
    has_field('street_typ', String(4), key='sttype')
    has_field('suf_dir', String(2), key='suffix')

    # To cities table
    has_field('city', Integer, key='city_l')
    has_field('city_r', Integer, default=0)

    # To places table
    has_field('l_zip', Integer, key='zip_code_l')
    has_field('r_zip', Integer, key='zip_code_r')

    # To edge table (supplemental)
    # None?

