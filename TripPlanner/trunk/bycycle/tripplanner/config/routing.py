import os
from routes import Mapper


def make_map(global_conf={}, app_conf={}):
    root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    mapper = Mapper(directory=os.path.join(root_path, 'controllers'))
    mapper.minimization = True

    # This route handles displaying the error page and graphics used in the
    # 404/500 error pages. It should likely stay at the top to ensure that the
    # error page is displayed properly.
    mapper.connect('error/{action}/{id}', controller='error')

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
    mapper.resource('ad', 'ads', **options)

    mapper.connect('info', 'http://info.bycycle.org/', _static=True)
    mapper.connect('about', 'http://info.bycycle.org/about/', _static=True)
    mapper.connect('help', 'http://info.bycycle.org/help/', _static=True)
    mapper.connect('gpl', 'http://info.bycycle.org/gplv3/', _static=True)
    mapper.connect('code', 'http://guest:guest@code.bycycle.org/', _static=True)
    mapper.connect('project', 'http://project.bycycle.org/', _static=True)

    # This one can be used to display a template directly
    mapper.connect('*url', controller='template', action='view')

    return mapper
