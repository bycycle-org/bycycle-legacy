import simplejson

from tripplanner.lib.base import *


class RestController(BaseController):
    """Base class for RESTful controllers."""

    def __init__(self):
        """Set up REST Controller.

        We assume the controller file is named after the resource's collection
        name and that there is a corresponding top level template directory.
        For example, for a Hat resource, the controller file will be named
        hats.py and there will be a template directory at /templates/hats.

        """
        route_info = request.environ['pylons.routes_dict']
        self.parent_id = route_info.get('parent_id', None)
        self.controller = route_info['controller']
        self.action = route_info['action']

        # Get parent name and parent Entity class for nested controller
        self.parent_name = getattr(self, 'parent_name', None)
        if self.parent_name:
            parent_entity_name = ''.join([word.title() for word in
                                          self.parent_name.split('_')])
            self.ParentEntity = getattr(model, parent_entity_name)
        else:
            parent_entity_name = None
            self.ParentEntity = None

        # The collection name should be the same as the controller's file name
        self.collection_name = self.controller

        # If ``member_name`` is explicitly set, use it; else, guess that the
        # member name is simply the collection name with an "s" hacked off.
        # TODO: Find better way to get member name when it's not explicitly
        # set.
        self.member_name = getattr(self, 'member_name',
                                   self.collection_name[0:-1])

        # TODO: Is there a library in Paste/Pylons that will do this
        # conversion from under_score to UnderScore?
        entity_name = ''.join([word.title() for word in
                               self.member_name.split('_')])

        # Import the entity class for the resource
        # This is sorta like ``from model import entity_name``
        self.Entity = getattr(model, entity_name)

        # Context:
        # route
        c.controller = self.controller
        c.action = self.action
        # parent
        c.parent_name = self.parent_name
        c.parent_entity_name = parent_entity_name
        # member
        c.collection_name = self.collection_name
        c.member_name = self.member_name
        c.entity_name = entity_name

    def index(self, parent_id=None, format=None):
        """GET /

        Show all (or subset of) items in collection.

        ``parent_id``
            The ID of the parent resource, if this is a nested resource. This
            is used to limit the collection to just those objects having a
            parent with this ID.

        """
        self._set_collection(parent_id)
        return self._render_response(format)

    def new(self, parent_id=None, format=None):
        """GET /resource/new

        Show a form for creating a new item. The form should POST to
        /resource/create.

        ``parent_id``
            If given, the new item's parent will be the object of the
            ``ParentEntity`` class having that ID.

        """
        self._set_member(parent_id)
        return self._render_response(format)

    def show(self, parent_id=None, id=None, format=None):
        """GET /resource/id

        Show existing item that has parent ID ``parent_id`` and ID ``id``.

        """
        self._set_member(parent_id, id)
        return self._render_response(format)

    def edit(self, parent_id=None, id=None, format=None):
        """GET /resource/id;edit

        Show a form for editing an existing item that has parent ID
        ``parent_id`` and ID ``id``. The form should PUT to /resource/update.

        """
        self._set_member(parent_id, id)
        return self._render_response(format)

    def create(self, parent_id=None, format=None):
        """POST /resource

        Create with POST data a new item that has parent ID ``parent_id``.

        """
        self._set_member(parent_id)

        # TODO: Add POST data to self.member here

        self.Entity.flush([self.member])
        redirect_to(id=self.member.id, parent_id=parent_id, format=format,
                    action='show')

    def update(self, parent_id=None, id=None, format=None):
        """PUT /resource/id

        Update with PUT data an existing item that has parent ID ``parent_id``
        and ID ``id`` .

        """
        self._set_member(parent_id, id)

        # TODO: Update self.member with PUT data here

        self.Entity.flush([self.member])
        redirect_to(parent_id=parent_id, id=id, format=format, action='show')

    def delete(self, parent_id=None, id=None, format=None):
        """DELETE /resource/id

        Delete the existing item that has parent_id ``parent_id`` ID ``id``.

        """
        self._set_member(parent_id, id)
        self.Entity.delete(self.member)
        self.Entity.flush([self.member])
        redirect_to(parent_id=parent_id, format=format, action='index')

    def _setattr(self, name, value):
        """Set attribute on ``c`` and ``self``.

        ``name``
            The name of the attribute

        ``value``
            The value of the attribute

        """
        setattr(self, name, value)
        setattr(c, name, value)

    def _set_parent(self, parent_id=None):
        """Set parent attribute on both ``self`` and ``c``.

        The member is attached as parent_name, where parent_name is specified
        in the child controller (defaults to "parent").

        """
        if self.ParentEntity and parent_id is not None:
            parent = self.ParentEntity.get(parent_id)
        else:
            parent = None
        self.parent = parent
        self._setattr(self.parent_name or 'parent', parent)

    def _set_member(self, parent_id=None, id=None):
        """Set member attribute on both ``self`` and ``c``.

        The member is attached as member_name, where member_name is the
        singular form of the resource.

        ``parent_id``
            The ID of the parent resource, if this is a nested resource

        ``id``
            The ID of the member to attach

        """
        self._set_parent(parent_id)
        if id is None:
            member = self.Entity()
        else:
            member = self.Entity.get(id)
        self.member = member
        self._setattr(self.member_name, member)

    def _set_collection(self, parent_id=None, page=0, num_items=10):
        """Set collection (or subset) attribute on both ``self`` and ``c``.

        The collection is attached as collection_name, where collection_name
        is the plural form of the resource.

        ``parent_id``
            The ID of the parent resource, if this is a nested resource

        ``page``
        ``num_items``
            Unimplemented for now
            TODO: Is there something in WebHelpers that can handle pagination?

        """
        self._set_parent(parent_id)
        self.collection = self.Entity.select()
        self._setattr(self.collection_name, self.collection)

    def _render_response(self, format='html', template=None, **response_args):
        """Renders a response for those actions that return content.

        ``format``
            The format of the response content

        ``template``
            An alternative template; by default, a template named after the
            action is used

        ``response_args``
            The remaining keyword args will be passed to the `Response`
            costructor

        return `Response`

        """
        # Dynamically determine the content method
        format = str(format or 'html').strip().lower()
        _get_content = getattr(self, '_get_%s_content' % (format))

        # _get_*_content methods need to add the file extension (if needed)
        tmpl = (template or self.action)
        self.template = '/%s/%s' % (self.collection_name, tmpl)

        content, mimetype = _get_content()
        response_args.update(dict(content=content, mimetype=mimetype))
        response = Response(**response_args)
        return response

    def _get_text_content(self):
        """Get plain text content and mimetype."""
        text = render('%s.txt' % self.template)
        return text, 'text/plain'
    _get_txt_content = _get_text_content

    def _get_json_content(self, obj_func=None):
        """Get a JSON string and mimetype "text/javascript".

        Assumes members have a __simplify__ method that returns an object
        that can be JSONified by the simplejson module. That object is
        JSONified and returned unless the ``obj_fun`` arg is supplied.

        ``obj_func``
            This method creates the simplest possible object to be JSONified
            (``obj``) by calling __simplify__ on a member or members. If a
            function is passed function via ``obj_func``, that function will
            be called with ``obj``, and ``obj`` can be modified there before
            being JSONified here.

        """
        try:
            member = getattr(self, self.member_name)
        except AttributeError:
            try:
                collection = getattr(self, self.collection_name)
            except AttributeError:
                obj = None
            else:
                obj = [m.__simplify__() for m in collection]
        else:
            obj = member.__simplify__()
        if obj_func is not None:
            obj = obj_func(obj)
        json = self._jsonify(obj)
        return json, 'text/javascript'

    def _jsonify(self, obj):
        """Convert a Python object to a JSON string.

        The object, ``obj``, must be "simple"--that is, it may consist of only
        tuples, list, dicts, numbers, and strings (and other built-in types,
        too?).

        """
        return simplejson.dumps(obj)

    def _get_html_content(self):
        """Get HTML content and mimetype."""
        html = render('%s.html' % self.template)
        return html, 'text/html'

    def _get_fragment_content(self):
        """Get an HTML fragment and mimetype."""
        html = render('%s.frag' % self.template)
        return html, 'text/html'
    _get_frag_content = _get_fragment_content

    def _get_xml_content(self):
        """Get XML content."""
        raise ValueError('Sorry, XML not spoken here.')
