"""Pylons middleware initialization"""
from paste.cascade import Cascade
from paste.registry import RegistryManager
from paste.urlparser import StaticURLParser
from paste.deploy.converters import asbool

from pylons import config
from pylons.error import error_template
from pylons.middleware import error_mapper, ErrorDocuments, ErrorHandler, \
    StaticJavascripts
from pylons.wsgiapp import PylonsApp

from tripplanner.config.environment import load_environment

def make_app(global_conf, full_stack=True, **app_conf):
    """Create a Pylons WSGI application and return it

    `global_conf`
        The inherited configuration for this application. Normally from the
        [DEFAULT] section of the Paste ini file.

    `full_stack`
        Whether or not this application provides a full WSGI stack (by default,
        meaning it handles its own exceptions and errors). Disable full_stack
        when this application is "managed" by another WSGI middleware.

    `app_conf`
        The application's local configuration. Normally specified in the
        [app:<name>] section of the Paste ini file (where <name> defaults to
        main).
    """
    # Configure the Pylons environment
    load_environment(global_conf, app_conf)

    # The Pylons WSGI app
    app = PylonsApp()
    g = app.globals

    if asbool(full_stack):
        # Handle Python exceptions
        app = ErrorHandler(app, global_conf, error_template=error_template,
                           **config['pylons.errorware'])
        g.error_handler = app

    # Establish the Registry for this application
    app = RegistryManager(app)

    if g.debug:
        static_app = StaticURLParser(config.paths['static_files'])
        javascripts_app = StaticJavascripts()
        app = Cascade([static_app, javascripts_app, app])

    return app
