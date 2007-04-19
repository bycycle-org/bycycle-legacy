from tripplanner.lib.base import *


class RestController(BaseController):
    """Base class for ReSTful resource controllers."""

    #----------------------------------------------------------------------
    def index(self):
        """Redirect to `show`."""
        p = request.params
        q = p.get('q', None)

    #----------------------------------------------------------------------
    def show(self, id, **params):
        """Query back end service with q = ``id``."""
        raise NotImplementedError

    #----------------------------------------------------------------------
    def create(self):
        raise NotImplementedError

    #----------------------------------------------------------------------
    def update(self, id):
        raise NotImplementedError

    #----------------------------------------------------------------------
    def delete(self, id):
        raise NotImplementedError

    #----------------------------------------------------------------------
    def edit(self, id):
        raise NotImplementedError
