# TODO: move to lib.base???
from tripplanner.lib.base import *


class RestController(BaseController):
    """Base class for RESTful controllers."""

    def __init__(self):
        """Set up REST Controller.

        We assume the controller file is named after the resource's collection
        name and that there is a corresponding top level template directory.
        For example for a Pants resource the controller file will be named
        pants.py and there will be a template directory at /templates/pants.

        """
        route_info = request.environ['pylons.routes_dict']
        self.controller = route_info['controller']
        self.action = route_info['action']

        # The collection name should be the same as the controller's file name
        self.collection_name = self.controller
        
        # If ``member_name`` is explicitly set, use it; else, guess that the
        # member name is simply the collection name with an "s" hacked off.
        # TODO: Find better way to get member name when it's not explicitly set.
        self.member_name = getattr(self, 'member_name', self.collection_name[0:-1])
        
        c.controller = self.controller
        c.action = self.action
        c.collection_name = self.collection_name
        c.member_name = self.member_name

    def _render_response(self, format):
        """Renders a response for those actions that return content.

        ``format`` -- The format of the response content

        """
        if format is None:
            # The default is to render the HTML template in the
            # /templates/collection_name directory that corresponds to
            # ``self.action``
            return render_response('/%s/%s.html' % 
                                   (self.collection_name, self.action))
        else:
            raise NotImplementedError

    def index(self, format=None):
        """GET / 
        
        Show all items in collection.
        
        """
        setattr(c, self.collection_name, [])  # Fetch all Objects in collection
        return self._render_response(format)

    def new(self, format=None):
        """GET /resource/new

        Show a form for creating a new item. The form should POST to
        /resource/create.

        """
        setattr(c, self.member_name, None)  # a new empty Object
        return self._render_response(format)

    def show(self, id, format=None):
        """GET /resource/id

        Show existing item having ID ``id``.

        """
        setattr(c, self.member_name, None)  # Object with ``id``
        return self._render_response(format)

    def edit(self, id, format=None):
        """GET /resource/id;edit

        Show a form for editing existing item having ID ``id``. The form
        should PUT to /resource/update.

        """
        setattr(c, self.member_name, None)  # Object with ``id``
        return self._render_response(format)

    def create(self):
        """POST /resource

        Create a new item with POST data.

        """
        raise NotImplementedError

    def update(self, id):
        """PUT /resource/id

        Update existing item having ID ``id`` with PUT data.

        """
        setattr(c, self.member_name, None)  # Object with ``id``

    def delete(self, id):
        """DELETE /resource/id

        Delete existing item having ID ``id``.

        """
        raise NotImplementedError
