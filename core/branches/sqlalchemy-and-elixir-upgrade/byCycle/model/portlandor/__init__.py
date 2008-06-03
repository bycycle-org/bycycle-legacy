###############################################################################
# $Id$
# Created 2005-11-07
#
# Portland, OR, region.
#
# Copyright (C) 2006 Wyatt Baldwin, byCycle.org <wyatt@bycycle.org>.
# All rights reserved.
#
# For terms of use and warranty details, please see the LICENSE file included
# in the top level of this distribution. This software is provided AS IS with
# NO WARRANTY OF ANY KIND.
###############################################################################
from sqlalchemy import MetaData

from elixir import options_defaults
from elixir import Entity, Field
from elixir import Unicode, Integer, String, CHAR, Integer, Numeric, Float

from byCycle.model import db
from byCycle.model.entities import base
from byCycle.model.entities.util import encodeFloat
from byCycle.model.data.sqltypes import POINT, LINESTRING
from byCycle.model.portlandor.data import SRID, slug

from dijkstar import infinity

__all__ = ['Edge', 'Node', 'StreetName', 'City', 'State', 'Place']


options_defaults['shortnames'] = True
options_defaults['inheritance'] = 'multi'
options_defaults['table_options']['schema'] = slug

metadata = db.metadata_factory()


class Edge(base.Edge):
    geom = Field(LINESTRING(SRID))
    permanent_id = Field(Numeric(11, 2))
    code = Field(Integer)
    bikemode = Field(CHAR(1))  # enum('','p','t','b','l','m','h','c','x')
    up_frac = Field(Float)
    abs_slope = Field(Float)
    cpd = Field(Integer)
    sscode = Field(Integer)

    def to_feet(self):
        return self.geom.length()

    def to_miles(self):
        return self.to_feet() / 5280.0

    def to_kilometers(self):
        return self.to_miles() * 1.609344

    def to_meters(self):
        return self.to_kilometers() * 1000.0

    @classmethod
    def _adjustRowForMatrix(cls, row):
        adjustments = {
            'length': encodeFloat(row.geom.length() / 5280.0),
            'abs_slope': encodeFloat(row.abs_slope),
            'up_frac': encodeFloat(row.up_frac),
        }
        return adjustments


class Node(base.Node):
    geom = Field(POINT(SRID))

    @property
    def edges(self):
        return super(Node, self).edges


class StreetName(base.StreetName):
    pass


class City(base.City): pass


class State(base.State):
    pass


class Place(base.Place):
    pass