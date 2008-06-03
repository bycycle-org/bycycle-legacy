from sqlalchemy import *
from elixir import *
from byCycle.model.data.sqltypes import POINT, LINESTRING


options_defaults['shortnames'] = True

metadata = MetaData()
engine = create_engine('postgres://bycycle:pants@localhost/bycycle')
metadata.connect(engine)


class Agency(Entity):
    """\copy trimet.agency (agency_name,agency_url,agency_timezone) FROM /home/bycycle/byCycle/core/trunk/byCycle/model/trimet/google_transit/agency.txt CSV HEADER"""
    using_table_options(schema='trimet')
    has_field('agency_name', Unicode(255))
    has_field('agency_url', Unicode(255))
    has_field('agency_timezone', Unicode(255))


class Shape(Entity):
    """\copy trimet.shape (shape_id,shape_pt_lat,shape_pt_lon,shape_pt_sequence,shape_dist_traveled) FROM /home/bycycle/byCycle/core/trunk/byCycle/model/trimet/google_transit/shapes.txt CSV HEADER"""
    using_table_options(schema='trimet')
    has_field('shape_id', Integer)
    has_field('shape_pt_lat', Float)
    has_field('shape_pt_lon', Float)
    has_field('shape_pt_sequence', Integer)
    has_field('shape_dist_traveled', Integer)
    has_field('geom', POINT(4326))


class Route(Entity):
    """\copy trimet.route (route_id,route_short_name,route_long_name,route_type,route_url) FROM /home/bycycle/byCycle/core/trunk/byCycle/model/trimet/google_transit/routes.txt CSV HEADER"""
    using_table_options(schema='trimet')
    has_field('id', Integer, primary_key=True)
    has_field('route_short_name', Integer)
    has_field('route_long_name', Unicode(255))
    has_field('route_type', Integer)
    has_field('route_url', Unicode(255))


class FareAttribute(Entity):
    """\copy trimet.fareattribute (fare_id,price,currency_type,payment_method,transfers,transfer_duration) FROM /home/bycycle/byCycle/core/trunk/byCycle/model/trimet/google_transit/fare_attributes.txt CSV HEADER"""
    using_table_options(schema='trimet')
    has_field('id', Integer, primary_key=True)
    has_field('price', Numeric(4, 2))
    has_field('currency_type', CHAR(3))
    has_field('payment_method', Integer)
    has_field('transfers', Integer)
    has_field('transfer_duration', Integer)  # seconds


class CalendarDate(Entity):
    """\copy trimet.calendardate (service_id,date,exception_type) FROM /home/bycycle/byCycle/core/trunk/byCycle/model/trimet/google_transit/calendar_dates.txt CSV HEADER"""
    using_table_options(schema='trimet')
    #belongs_to('service', of_kind='Calendar')
    has_field('date', Date)
    has_field('exception_type', Integer)


class Stop(Entity):
    """\copy trimet.stop (stop_id,stop_name,stop_lat,stop_lon,zone_id) FROM /home/bycycle/byCycle/core/trunk/byCycle/model/trimet/google_transit/stops.txt CSV HEADER"""
    using_table_options(schema='trimet')
    has_field('id', Integer, primary_key=True)
    has_field('stop_name', Unicode(255))
    has_field('stop_lat', Float)
    has_field('stop_lon', Float)
    has_field('zone_id', Integer)


class FareRule(Entity):
    using_table_options(schema='trimet')
    belongs_to('fare', of_kind='FareAttribute')
    belongs_to('route', of_kind='Route')
    belongs_to('origin', of_kind='Stop')
    belongs_to('destination', of_kind='Stop')


class Trip(Entity):
    using_table_options(schema='trimet')
    belongs_to('route', of_kind='Route')
    #belongs_to('service', of_kind='Calendar')
    has_field('id', CHAR(9), primary_key=True)
    has_field('direction_id', Integer)
    has_field('block_id', Integer)
    has_field('shape_id', Integer)


class StopTime(Entity):
    using_table_options(schema='trimet')
    belongs_to('trip', of_kind='Trip')
    has_field('arrival_time', Time)
    has_field('departure_time', Time)
    belongs_to('stop', of_kind='Stop')
    has_field('stop_sequence', Integer)
    has_field('stop_headsign', Unicode(255))
    has_field('pickup_type', Integer)
    has_field('drop_off_type', Integer)
    has_field('shape_dist_traveled', Integer)


if __name__ == '__main__':
    import sys
    from byCycle import model
    try:
        action = sys.argv[1]
    except IndexError:
        print 'No action'
    else:
        print 'Action: %s' % action
        try: args = sys.argv[2:]
        except IndexError: args = []
        eval(action)(*args)


"""
No Dependencies
---------------

agency.txt
agency_name,agency_url,agency_timezone

shapes.txt
shape_id,shape_pt_lat,shape_pt_lon,shape_pt_sequence,shape_dist_traveled

routes.txt
route_id,route_short_name,route_long_name,route_type,route_url

fare_attributes.txt
fare_id,price,currency_type,payment_method,transfers,transfer_duration

calendar_dates.txt
service_id,date,exception_type


Dependencies
------------

stops.txt
stop_id,stop_name,stop_lat,stop_lon,zone_id

fare_rules.txt
fare_id,route_id,origin_id,destination_id

trips.txt
route_id,service_id,trip_id,direction_id,block_id,shape_id

stop_times.txt
trip_id,arrival_time,departure_time,stop_id,stop_sequence,stop_headsign,pickup_type,drop_off_type,shape_dist_traveled

"""
