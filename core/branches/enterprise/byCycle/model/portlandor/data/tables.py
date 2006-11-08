###########################################################################
# $Id: tables.py 187 2006-08-16 01:26:11Z bycycle $
# Created 2006-09-07
#
# Portland, OR, table definitions
#
# Copyright (C) 2006 Wyatt Baldwin, byCycle.org <wyatt@bycycle.org>.
# All rights reserved.
#
# For terms of use and warranty details, please see the LICENSE file included
# in the top level of this distribution. This software is provided AS IS with
# NO WARRANTY OF ANY KIND.


from sqlalchemy.schema import Table, Column, ForeignKey
from sqlalchemy.types import String, CHAR, Integer, Numeric, Float
from byCycle.model import portlandor
from byCycle.model.data.sqltypes import *


SRID = portlandor.SRID


class Tables(object):
    """Tables for the Portland, OR, region."""

    def __init__(self, schema, metadata, raw_metadata, add_geometry=True):
        """Initialize tables for ``schema``, associating them with ``metadata``.

        ``metadata`` `object` -- SQLAlchemy `MetaData`
        
        ``schema`` `string` -- Database schema name (typically, the region name)
        
        ``add_geometry`` `bool` -- Whether of not to add the geometry columns.
        Normally, we want to add the geometry columns, but not always.
        
        """
        self.metadata = metadata
        self.raw_metadata = raw_metadata
        self.schema = schema
        self.__initTables(add_geometry=add_geometry)

    def __getitem__(self, key):
        """Allow access to tables using `dict` notation."""
        if name in self.__table_names:
            return self.__dict__[key]
        else:
            raise KeyError('%s is not a table in the %s schema.' % 
                           (key, self.schema))

    def __initTables(self, add_geometry=True):
        """Create table definitions for region, adding them as attrs of self.

        ``add_geometry`` `bool` -- See __init__.

        """
        metadata = self.metadata
        schema = self.schema
        tables = (
            Table(
                'layer_edges',
                metadata,
                Column('id', Integer, primary_key=True),

                Column('node_f_id', Integer,
                       ForeignKey('layer_nodes.id'),
                       nullable=False),
                Column('node_t_id', Integer,
                       ForeignKey('layer_nodes.id'),
                       nullable=False),

                Column('addr_f', Integer),
                Column('addr_t', Integer),

                # enum('l','r', NULL)
                Column('even_side', CHAR(1)),

                Column('street_name_id',Integer,ForeignKey('street_names.id')),

                Column('city_l_id', Integer, ForeignKey('cities.id')),
                Column('city_r_id', Integer, ForeignKey('cities.id')),

                Column('state_l_id', CHAR(2), ForeignKey('states.id'),
                       nullable=False),
                Column('state_r_id', CHAR(2), ForeignKey('states.id'),
                       nullable=False),

                Column('zip_code_l', Integer),
                Column('zip_code_r', Integer),

                Column('localid', Numeric(11, 2) , nullable=False),
                Column('one_way', Integer, nullable=False),
                Column('code', Integer, nullable=False),

                #enum('','p','t','b','l','m','h','c','x'),
                Column('bikemode', CHAR(1)),

                Column('up_frac', Float, nullable=False),
                Column('abs_slp', Float, nullable=False),
                Column('cpd', Integer),
                Column('sscode', Integer),

                schema=schema,
                ),

            Table(
                'layer_nodes',
                metadata,
                Column('id', Integer, primary_key=True),
                schema=schema,
                ),

            Table(
                'street_names',
                metadata,
                Column('id', Integer, primary_key=True),
                Column('prefix', String(2)),
                Column('name', String, nullable=False),
                Column('sttype', String(4)),
                Column('suffix', String(2)),
                schema=schema,
                ),

            Table(
                'cities',
                metadata,
                Column('id', Integer, primary_key=True),
                Column('city', String, nullable=False),
                schema=schema,
                ),

            Table(
                'states',
                metadata,
                Column('id', CHAR(2), primary_key=True),
                Column('state', String, nullable=False),
                schema=schema,
                )
            )
        self.__table_names = {}
        for table in tables:            
            name = table.name
            self.__table_names[name] = 1
            self.__dict__[name] = table
        if add_geometry:
            self._appendGeometryColumns()

    def _appendGeometryColumns(self):
        """Add geometry columns to layer tables."""
        tables = (self.layer_edges, self.layer_nodes)
        types = (LINESTRING, POINT)        
        for table, type_ in zip(tables, types):
            table.append_column(
                Column('geom', type_(SRID), nullable=False)
            )

    def _get_raw_table(self):
        """Return (creating if necessary) raw table definition for region.

        Raw tables are created in the raw schema, with the schema name as the
        table name. The raw table doesn't get created unless it's needed.

        return `Table` -- The raw table

        """
        try:
            return self._raw_table
        except AttributeError:
            self._raw_table = Table(
                self.schema,
                self.raw_metadata,
                Column('gid', Integer, primary_key=True),

                # To edge table (core)
                Column('the_geom', LINESTRING(SRID)),
                Column('n0', Integer),
                Column('n1', Integer),
                Column('zipcolef', Integer),
                Column('zipcorgt', Integer),

                # To edge table after being unified (core)
                Column('leftadd1', Integer),
                Column('leftadd2', Integer),
                Column('rgtadd1', Integer),
                Column('rgtadd2', Integer),

                # To edge table (supplemental)
                Column('localid', Float),
                Column('type', Integer),
                Column('bikemode', String(2)),
                Column('upfrc', Float),
                Column('abslp', Float),
                Column('one_way', String(2)),
                Column('sscode', Integer),
                Column('cpd', Integer),

                # To street names table
                Column('fdpre', String(2)),
                Column('fname', String(30)),
                Column('ftype', String(4)),
                Column('fdsuf', String(2)),

                # To cities table
                Column('lcity', String(4)),
                Column('rcity', String(4)),

                schema='raw',
                )
            return self._raw_table
    raw_table = property(_get_raw_table)
