"""The application's Globals object"""
from pylons import config
from paste.deploy.converters import asbool


class Globals(object):
    """Globals acts as a container for objects available throughout the life of
    the application.
    """

    def __init__(self):
        """One instance of Globals is created during application initialization
        and is available during requests via the 'g' variable.
        """
        self.debug = asbool(config.get('debug', False))