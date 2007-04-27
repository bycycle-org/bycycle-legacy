from elixir import Entity
from elixir import options_defaults, using_options, using_table_options
from elixir import has_field
from elixir import belongs_to, has_one, has_many, has_and_belongs_to_many
from elixir import Unicode, Integer, String, CHAR, Integer, Numeric, Float


from byCycle.model.domain import cascade_args, encodeFloat, decodeFloat
from byCycle.model.data.sqltypes import POINT, LINESTRING
from byCycle.model.portlandor.data import SRID


class Edge(Entity):
    using_options(tablename='portlandor_edge')
    has_field('geom', LINESTRING(SRID))
    has_field('localid', Numeric(11, 2) )
    has_field('code', Integer)
    has_field('bikemode', CHAR(1))  # enum('','p','t','b','l','m','h','c','x')
    has_field('up_frac', Float)
    has_field('abs_slope', Float)
    has_field('cpd', Integer)
    has_field('sscode', Integer)
    belongs_to('base', of_kind='byCycle.model.domain.Edge', **cascade_args)

    def to_feet(self):
        return self.geom.length()

    def to_miles(self):
        return self.geom.length() / 5280.0

    def to_kilometers(self):
        return self.geom.length() / 5280.0 * 1.609344

    def to_meters(self):
        return self.geom.length() / 5280.0 * 1.609344 / 1000.0

    @classmethod
    def _getRowsForMatrix(cls):
        code = cls.c.code
        region_rows = cls.table.select((
            ((code >= 1200) & (code < 1600)) |
            ((code >= 3200) & (code < 3300))
        )).execute()
        return region_rows

    @classmethod
    def _adjustRowForMatrix(cls, row):
        adjustments = {
            'abs_slope': encodeFloat(row.abs_slope),
            'up_frac': encodeFloat(row.up_frac),
        }
        return adjustments


class Node(Entity):
    using_options(tablename='portlandor_node')
    has_field('geom', POINT(SRID))
    belongs_to('base', of_kind='byCycle.model.domain.Node', **cascade_args)

    @property
    def edges(self):
        return self.base.edges
