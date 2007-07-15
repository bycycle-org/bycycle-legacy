###############################################################################
# $Id: __init__.py 918 2007-05-25 18:48:44Z bycycle $
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

from elixir import Entity, options_defaults, has_field
from elixir import Unicode, Integer, String, CHAR, Integer, Numeric, Float

from byCycle.model import db
from byCycle.model.entities import base
from byCycle.model.entities.base import base_statements
from byCycle.model.entities.util import encodeFloat
from byCycle.model.data.sqltypes import POINT, LINESTRING
from byCycle.model.seattlewa.data import SRID, slug

__all__ = ['Edge', 'Node', 'StreetName', 'City', 'State', 'Place']


options_defaults['shortnames'] = True
options_defaults['inheritance'] = None
options_defaults['table_options']['schema'] = slug

metadata = db.metadata_factory(slug)


class Edge(base.Edge):
    base_statements('Edge')
    has_field('geom', LINESTRING(SRID))
    has_field('permanent_id', Integer)
    has_field('code', Integer)
    has_field('bikemode', Integer)  # enum('','p','t','b','l','m','h','c','x')

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
        return {}


class Node(base.Node):
    base_statements('Node')
    has_field('geom', POINT(SRID))

    @property
    def edges(self):
        return super(Node, self).edges


class StreetName(base.StreetName):
    base_statements('StreetName')


class City(base.City):
    base_statements('City')


class State(base.State):
    base_statements('State')


class Place(base.Place):
    base_statements('Place')