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
from sqlalchemy.schema import *
from sqlalchemy.types import *
from byCycle.model.data.sqltypes import *


def createRawTable(metadata, table_name):
    """Create and return raw table for region.
    
    Raw tables are created in the raw schema, with the region name as the 
    table name.
    
    ``metadata`` `object`
        SQLAlchemy BoundMetaData
        
    ``table_name`` `string`
        Name of raw table (typically, the region name)

    Return `Tables`
        A simple object that allows access to the schema tables using dot
        notation
        
    """
    raw_table = Table(
        table_name,
        metadata,
        Column('gid', Integer, primary_key=True),

        # To street layer table (core)
        Column('the_geom', Geometry),
        Column('fnode', Integer),
        Column('tnode', Integer),
        Column('zipcolef', Integer),
        Column('zipcorgt', Integer),

        # To street layer table after being unified (core)
        Column('leftadd1', Integer),
        Column('leftadd2', Integer),
        Column('rgtadd1', Integer),
        Column('rgtadd2', Integer),

        # To street layer table (supplemental)
        Column('localid', Float),
        Column('type', Integer),
        Column('bikemode', String(2)),
        Column('up_frac', Float),
        Column('abs_slp', Float),
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

        # TODO: To counties table???
        #Column('lcounty', String(4)),
        #Column('rcounty', String(4)),

        # Unused
        #Column('drct', Integer),
        #Column('length', Integer),
        #Column('ix', Integer),
        #Column('f_elev', Integer),
        #Column('t_elev', Integer),
        #Column('ft_base', Float),
        #Column('tf_base', Float),
        #Column('maj', String(1)),
        #Column('dzp', Integer),
        #Column('dzn', Integer),
        #Column('grnd', Integer),
        
        schema='raw',
        )
    return raw_table


def createSchemaTables(metadata, schema):
    """Create and return tables for region.
    
    ``metadata`` `object`
        SQLAlchemy BoundMetaData
        
    ``schema`` `string`
        Database schema name (typically, the region name)

    Return `dict`
        table name => table object
        
    """
    tables = (
        Table(
            'layer_streets',
            metadata,
            Column('id', Integer, primary_key=True),
            Column('geom', Geometry, nullable=False),
            
            Column('node_f_id', Integer, 
                   ForeignKey('layer_nodes.id'),
                   nullable=False),  
            Column('node_t_id', Integer, 
                   ForeignKey('layer_nodes.id'),
                   nullable=False),
            
            Column('addr_f', Integer),
            Column('addr_t', Integer),
            
            # enum('l','r')
            Column('even_side', String(1)),
            
            Column('street_name_id', Integer, ForeignKey('street_names.id'),),
            
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
            Column('bikemode', String(1), nullable=False),
             
            Column('up_frac', Numeric(4, 3), nullable=False),
            Column('abs_slp', Numeric(4, 3), nullable=False),
            Column('cpd', Integer),
            Column('sscode', Integer),
            
            schema=schema,
            ),
        
        Table(
            'layer_nodes',
            metadata,
            Column('id', Integer, primary_key=True),
            Column('geom', Geometry, nullable=False),
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
    
    class Tables(object):
        def __init__(self, tables=()):
            for table in tables:
                self.__dict__[table.name] = table   
    return Tables(tables)
    
