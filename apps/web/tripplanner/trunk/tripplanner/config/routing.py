from pylons import config
from routes import Mapper

def make_map():
    """Create, configure and return the routes Mapper"""
    mapper = Mapper(directory=config['pylons.paths']['controllers'],
                    always_scan=config['debug'])

    # The ErrorController route (handles 404/500 error pages); it should
    # likely stay at the top, ensuring it can always be resolved
    mapper.connect('error/:action/:id', controller='error')

    # Default route => Show list of regions
    mapper.connect('', controller='regions', _collection_name='regions',
                   _member_name='region')

    mapper.resource('region', 'regions', collection=dict(find='GET'))

    # Service routes
    options = dict(
        collection=dict(find='GET'),
        parent_resource=dict(member_name='region', collection_name='regions'),
        name_prefix='',
    )
    mapper.resource('service', 'services', **options)
    mapper.resource('geocode', 'geocodes', **options)
    mapper.resource('route', 'routes', **options)

    mapper.connect('*url', controller='template', action='view')

    return mapper
