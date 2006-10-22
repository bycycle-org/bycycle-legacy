import sqlalchemy
from cartography.spatial import geometry
from cartography.referencing.srs import SpatialReference
from binascii import a2b_hex, b2a_hex


class Geometry(sqlalchemy.types.TypeEngine):
    """PostGIS Geometry Type."""
    
    def __init__(self, SRID, type_, dimension):
        """
        
        ``SRID`` `int` -- Spatial Reference ID
        ``type_`` `string` -- Geometry type (POINT, LINESTRING, etc)
        ``dimension`` `int` -- Geometry dimensions (2D, 3D, etc)
        
        From PostGIS documentation:
        
        AddGeometryColumn(
            <schema_name>, <table_name>, <column_name>, <SRID>, <type>,
            <dimension>
        )
        
        Example:
        
        AddGeometryColumn(        
            'portlandor', 'layer_edges', 'geom', 2913, 'MULTILINESTRING', 2
        )
        
        First three params are given; we need to get the last three from the
        users of this class.
        
        """
        self.SRID = SRID
        self.srs = SpatialReference(epsg=SRID)
        self.type = type_.upper()
        self.dimension = dimension
        
    def get_col_spec(self):
        """What exactly is this supposed to return?
        
        I *think* it's what goes in the table definition. If so, I think this
        is correct. AFAICT, PostGIS geometry types are defined by constraints.
        
        """
        return 'GEOMETRY'
    
    def convert_bind_param(self, value, engine):
        """Convert value from Python ==> database.
        
        ``value`` -- A geometry object of some kind. The database expects a 
        hex string representing a WKB geometry.
        
        """
        return b2a_hex(value.toWKB())
                
    def convert_result_value(self, value, engine):
        """Convert ``value`` from database ==> Python.

        ``value`` `string` -- PostGIS geometry value from the database. It is
        a hex string representing a WKB geometry.
        
        """
        g = geometry.Geometry.fromWKB(a2b_hex(value), srs=self.srs)
        return g


class MULTILINESTRING(Geometry):
    def __init__(self, SRID):
        Geometry.__init__(self, SRID, 'MULTILINESTRING', 2)

class LINESTRING(Geometry):
    def __init__(self, SRID):
        Geometry.__init__(self, SRID, 'LINESTRING', 2)

class POINT(Geometry):
    def __init__(self, SRID):
        Geometry.__init__(self, SRID, 'POINT', 2)

