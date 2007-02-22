from tripplanner.lib.base import *


class RestController(BaseController):
    """Base class for RESTful controllers."""

    def __init__(self):
        """Set up REST Controller.

        We assume the controller file is named after the resource's collection
        name and that there is a corresponding top level template directory.
        For example, for a Hat resource, the controller file will be named
        pants.py and there will be a template directory at /templates/hats.

        """
        route_info = request.environ['pylons.routes_dict']
        self.controller = route_info['controller']
        self.action = route_info['action']

        # The collection name should be the same as the controller's file name
        self.collection_name = self.controller
        
        # If ``member_name`` is explicitly set, use it; else, guess that the
        # member name is simply the collection name with an "s" hacked off.
        # TODO: Find better way to get member name when it's not explicitly
        # set.
        self.member_name = getattr(self, 'member_name', 
                                   self.collection_name[0:-1])
        
        c.controller = self.controller
        c.action = self.action
        c.collection_name = self.collection_name
        c.member_name = self.member_name

        # TODO: Is there a library in Paste/Pylons that will do this
        # conversion from under_score to UnderScore?
        entity_name = ''.join([word.title() for word in 
                               self.member_name.split('_')])

        # Import the entity class for the resource
        # This is sorta like ``from model import entity_name``
        self.Entity = getattr(model, entity_name)
        
        # Connect dynamic metadata to global DB engine (apparently needs to be
        # done on every request)
        model.connect()

    def _render_response(self, format=None, template=None):
        """Renders a response for those actions that return content.

        ``format`` -- The format of the response content
        
        ``template`` -- An alternative template; by default, a template named
        after the action is used.

        """
        if format is None:
            # The default is to render the HTML template in the
            # /templates/collection_name directory that corresponds to
            # ``self.action``
            return render_response('/%s/%s.html' % 
                                   (self.collection_name, 
                                    template or self.action))
        else:
            raise NotImplementedError
    
    def _set_member(self, id=None):
        if id is None:
            member = self.Entity()
        else:
            member = self.Entity.select(id)
        setattr(c, self.member_name, member)

    def _set_collection(self, page=0, num_items=10):
        collection = self.Entity.select()
        setattr(c, self.collection_name, collection)        
        
    def index(self, format=None):
        """GET / 
        
        Show all items in collection.
        
        """
        self._set_collection()
        return self._render_response(format)

    def new(self, format=None):
        """GET /resource/new

        Show a form for creating a new item. The form should POST to
        /resource/create.

        """
        self._set_member()
        return self._render_response(format)

    def show(self, id, format=None):
        """GET /resource/id

        Show existing item having ID ``id``.

        """
        print 'show'
        self._set_member(id)
        return self._render_response(format)

    def edit(self, id, format=None):
        """GET /resource/id;edit

        Show a form for editing existing item having ID ``id``. The form
        should PUT to /resource/update.

        """
        self._set_member(id)
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
        self._set_member(id)

    def delete(self, id):
        """DELETE /resource/id

        Delete existing item having ID ``id``.

        """
        raise NotImplementedError
