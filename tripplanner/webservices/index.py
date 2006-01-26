def index():
    result = 'byCycle Trip Planner Web Services<br/>' \
             'Available Services:<br/>' \
             '<a href="route">Routing</a><br/>' \
             '<a href="geocode">Geocoding</a>'
    return result


def geocode():
    return 'Geocode'


def route():
    return 'Route'
