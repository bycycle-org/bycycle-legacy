import os
from routes import Mapper


def make_map(global_conf={}, app_conf={}):
    root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    map_ = Mapper(directory=os.path.join(root_path, 'controllers'))

    # This route handles displaying the error page and graphics used in the
    # 404/500 error pages. It should likely stay at the top to ensure that the
    # error page is displayed properly.
    map_.connect('error/:action/:id', controller='error')

    map_.connect(
        ':region',
        controller='region',
        action='show',
        conditions=dict(method=['GET']),
    )
    
    # Define your routes. The more specific and detailed routes should be
    # defined first, so they may take precedent over the more generic routes.
    # For more information, refer to the routes manual @
    # http://routes.groovie.org/docs/

    # Default routes
    map_.connect(':controller/:action/:id')
    # This one can be used to display a template directly
    map_.connect('*url', controller='template', action='view')

    return map_
