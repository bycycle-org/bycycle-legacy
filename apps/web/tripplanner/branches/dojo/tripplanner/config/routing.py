import os
from routes import Mapper


def make_map(global_conf={}, app_conf={}):
    root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    mapper = Mapper(directory=os.path.join(root_path, 'controllers'))

    # This route handles displaying the error page and graphics used in the
    # 404/500 error pages. It should likely stay at the top to ensure that the
    # error page is displayed properly.
    mapper.connect('error/:action/:id', controller='error')

    # Default route => Show list of regions
    mapper.connect('', controller='regions')
    
    mapper.resource('region', 'regions')

    # Service routes
    options = dict(
        collection=dict(find='GET'),
        path_prefix='regions/:parent_id'
    )
    mapper.resource('service', 'services', **options)
    mapper.resource('geocode', 'geocodes', **options)
    mapper.resource('route', 'routes', **options)

    # This one can be used to display a template directly
    mapper.connect('*url', controller='template', action='view')

    return mapper
