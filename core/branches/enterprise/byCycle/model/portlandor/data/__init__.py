"""This package contains everything to do with this region's data and DB."""
from elixir import Entity, using_options, using_table_options
from elixir import has_field
from elixir import Integer, String, Integer, Float
from byCycle.model.data.sqltypes import MULTILINESTRING


title = 'Portland, OR, metro region'
slug = 'portlandor'
SRID = 2913
units = 'feet'
earth_circumference = 131484672
edge_attrs = ['code', 'bikemode', 'up_frac', 'abs_slope', 'cpd', 'sscode']


class Raw(Entity):
    using_options(tablename=slug)
    using_table_options(schema='raw')

    has_field('gid', Integer, primary_key=True, key='id')

    # To edge table (core)
    has_field('the_geom', MULTILINESTRING(SRID), key='geom')
    has_field('n0', Integer, key='node_f_id')
    has_field('n1', Integer, key='node_t_id')
    has_field('zipcolef', Integer, key='zip_code_l')
    has_field('zipcorgt', Integer, key='zip_code_r')

    # To edge table after being unified (core)
    has_field('leftadd1', Integer, key='addr_f_l')
    has_field('leftadd2', Integer, key='addr_t_l')
    has_field('rgtadd1', Integer, key='addr_f_r')
    has_field('rgtadd2', Integer, key='addr_t_r')

    # To edge table (supplemental)
    has_field('localid', Float)
    has_field('type', Integer, key='code')
    has_field('bikemode', String(2))
    has_field('upfrc', Float, key='up_frac')
    has_field('abslp', Float, key='abs_slope')
    has_field('one_way', String(2))
    has_field('sscode', Integer)
    has_field('cpd', Integer)

    # To street names table
    has_field('fdpre', String(2), key='prefix')
    has_field('fname', String(30), key='name')
    has_field('ftype', String(4), key='sttype')
    has_field('fdsuf', String(2), key='suffix')

    # To cities table
    has_field('lcity', String(4), key='city_l')
    has_field('rcity', String(4), key='city_r')
