################################################################################
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
################################################################################
from sqlalchemy.schema import Table, Column, ForeignKey
from sqlalchemy.types import String, CHAR, Integer, Numeric, Float
from byCycle.model import db
from byCycle.model.data.sqltypes import *


class Tables(object):

    def __init__(self, schema, SRID, metadata, append_geometry_columns=True):
        """Initialize tables for ``schema``, associating them with ``metadata``

        ``metadata``
            SQLAlchemy ``MetaData``

        ``schema``
            Database schema name (typically, the region name)

        ``append_geometry_columns``
            Whether of not to add the geometry columns. Normally, we want to
            add the geometry columns, but not always.

        """
        self.schema = schema
        self.SRID = SRID
        self.metadata = metadata
        self.__init_tables__(append_geometry_columns)

    def __init_tables__(self, append_geometry_columns):
        """Create table definitions, adding them as attrs of self."""
        metadata = self.metadata
        schema = self.schema
        # TODO: tables = self._table_defs(), then turn this into a base class
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
        for table in tables:
            setattr(self, table.name, table)
        if append_geometry_columns:
            self.append_geometry_columns()

    def create_geometry_columns(self):
        """Add geometry columns to database."""
        tables = (self.layer_edges, self.layer_nodes)
        types = ('LINESTRING', 'POINT')
        for table, type_ in zip(tables, types):
            db.addGeometryColumn(table, self.SRID, type_)

    def append_geometry_columns(self):
        """Append geometry columns to table definition."""
        tables = (self.layer_edges, self.layer_nodes)
        types = (LINESTRING, POINT)
        for table, type_ in zip(tables, types):
            table.append_column(
                Column('geom', type_(self.SRID), nullable=False)
            )

    def __getitem__(self, key):
        """Allow access to tables using dict notation."""
        try:
            return self.__dict__[key]
        except KeyError:
            raise KeyError('Unknown table: %s' % (key))

    @property
    def raw_table(self):
        """Return (creating if necessary) raw table definition for region.

        Raw tables are created in the raw schema, with the schema name as the
        table name. The raw table doesn't get created unless it's needed.

        return ``Table``
            The raw table

        """
        try:
            return self._raw_table
        except AttributeError:
            self._raw_table = Table(
                self.schema,
                self.metadata,
                Column('gid', Integer, primary_key=True),

                # To edge table (core)
                Column('the_geom', MULTILINESTRING(self.SRID)),
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
