from sqlalchemy import MetaData

from elixir import Entity
from elixir import options_defaults, using_options, using_table_options
from elixir import has_field
from elixir import belongs_to, has_one, has_many, has_and_belongs_to_many
from elixir import Unicode, Integer, String, CHAR, Integer, Numeric, Float

from byCycle.model import db, domain
from byCycle.model.domain import base_statements
from byCycle.model.domain import cascade_args, encodeFloat, decodeFloat
from byCycle.model.data.sqltypes import POINT, LINESTRING
from byCycle.model.portlandor.data import SRID, slug


options_defaults['shortnames'] = True
options_defaults['inheritance'] = None
options_defaults['table_options']['schema'] = slug

metadata = db.metadata_factory(slug)


class Edge(domain.Edge):
    base_statements('Edge')
    has_field('geom', LINESTRING(SRID))
    has_field('localid', Numeric(11, 2) )
    has_field('code', Integer)
    has_field('bikemode', CHAR(1))  # enum('','p','t','b','l','m','h','c','x')
    has_field('up_frac', Float)
    has_field('abs_slope', Float)
    has_field('cpd', Integer)
    has_field('sscode', Integer)

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
            'abs_slope': encodeFloat(row.abs_slope),
            'up_frac': encodeFloat(row.up_frac),
        }
        code = row.code
        if not ((1200 <= code < 1600) or (3200 <= code < 3300)):
            adjustments['length'] = 5280000
        return adjustments


class Node(domain.Node):
    base_statements('Node')
    has_field('geom', POINT(SRID))

    @property
    def edges(self):
        return super(Node, self).edges


class StreetName(domain.StreetName):
    base_statements('StreetName')


class City(domain.City):
    base_statements('City')


class State(domain.State):
    base_statements('State')


class Place(domain.Place):
    base_statements('Place')
