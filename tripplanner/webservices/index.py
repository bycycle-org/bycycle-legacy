# Web Services Index

def index():
    result = 'byCycle Trip Planner Web Services<br/>' \
             'Available Services:<br/>' \
             '<a href="route">Routing</a><br/>' \
             '<a href="geocode">Geocoding</a>'
    return result


def geocode():
    from byCycle.tripplanner.webservices import wsgeocode
    return 'geocode'

def route():
    from byCycle.tripplanner.webservices import wsroute
    return 'route'
