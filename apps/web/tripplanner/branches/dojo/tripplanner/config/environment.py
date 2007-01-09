from os.path import join, dirname, abspath
import pylons.config
from tripplanner.config.routing import make_map


def load_environment():
    map = make_map()

    # Set up our paths
    root_path = dirname(dirname(abspath(__file__)))
    template_paths = ('components', 'templates')
    paths = {
        'root_path': root_path,
        'controllers': join(root_path, 'controllers'),
        'templates': [join(root_path, path) for path in template_paths],
        'static_files': join(root_path, 'public')
    }

    # The following options are passed directly into Myghty, so all
    # configuration options available to the Myghty handler are available for
    # your use here. Add your own Myghty config options here, noting that all
    # config options will override any Pylons config options.
    myghty = {}
    myghty['log_errors'] = True

    # Return our loaded config object
    return pylons.config.Config(myghty, map, paths)
