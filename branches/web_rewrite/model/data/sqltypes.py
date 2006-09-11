import sqlalchemy


class Geometry(sqlalchemy.types.TypeDecorator):

    impl = sqlalchemy.types.Binary
    
    def convert_bind_param(self, value, engine):
        """Value from database."""
        return value
    
    def convert_result_value(self, value, engine):
        """Value from database."""
        return value

