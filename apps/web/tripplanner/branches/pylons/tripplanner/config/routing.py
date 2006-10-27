import sys, os
from routes import Mapper


def make_map():
    root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    m = Mapper(directory=os.path.join(root_path, 'controllers'))

    # Service -------------------------------------------------------------

    # /region/service/query => Query service in region (region may be "all")
    m.connect(
        ':region/:controller/:query',
        action='show',
        conditions=dict(method=['GET']),
    )

    # View ----------------------------------------------------------------

    # /                => Show all regions
    # /?params...      => Redirect according to params
    # /region          => Show specific region
    # /region/service => Show specific region with service form focused
    m.connect(
        ':region/:service',
        region=None,
        service=None,
        controller='region',
        action='show',
        conditions=dict(method=['GET']),
    )

    # Other ---------------------------------------------------------------

    m.connect('error/:action/:id', controller='error')

    # Catch-all for anything else
    # Shows an error page
    m.connect('*url', controller='view')

    return m



"""ReSTful Routes

    # Service routes ------------------------------------------------------

    # /query/some_query
    # Generic query
    m.resource('query')

    # /address/some_query
    m.resource('address')

    # /geocode/some_query
    m.resource('geocode')

    # /route/some_query
    m.resource('route')

    # Region routes -------------------------------------------------------

    # /region => Show all regions
    # /region/some_region => show region
    m.resource('region')

"""


#m.connect(':region', controller='root', action='region')
#m.connect(':service', controller='root', action='service',
#requirements=dict(service='query|address|geocode|route'))
#m.connect(':region/:action', controller='root', action='service')
#m.connect(':region/:service', controller='root', action='service',
#requirements=dict(service='query|address|geocode|route'))
#m.connect(':region/:service/:query', controller='root', action='query')
#m.connect(':region', controller='root', action='region')



    ## If there is *not* a query, use the view-only controller.
    ## All view-only requests are GETs

    ## Handle URLs where both a region and service are specified.
    #m.connect(
        #':region/:service',
        #controller='view',
        #action='get_regionAndService',
        #requirements=dict(
            #service='query|address|geocode|route'
            #),
        #conditions={'method': ['GET']},
    #)



    ## If there is a query, use a service controller. In this case the service
    ## in the URL is used for the controller name.
    ## TODO:
    ##   - Inherit from common Service controller
    ##   - Use HTTP request method to determine action
    #m.connect(
        ## Ex: /Portland,OR/Query/4807 SE Kelly to NE 6th & Irving
        ## Ex: /Portland,OR/Address/4807 SE Kelly
        ## Ex: /Portland,OR/Geocode/4807 SE Kelly
        ## Ex: /Portland,OR/Route/["4807 SE Kelly", "NE 6th & Irving"]
        #':region/:controller/:query',
        #action='get',
        #requirements=dict(
            #service='query|address|geocode|route'
            #),
        #conditions=dict(
            #method=['GET']
            #),
    #)



    ## Handle URLs where only a region is specified.
    #m.connect(
        #':region',
        #controller='view',
        #action='get_region',
        #conditions=dict(
            #method=['GET']
            #),
    #)
