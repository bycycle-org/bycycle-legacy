"""

Adds support for Rails-style RESTful ActiveRecord resources. Provides a
RESTful controller class that uses Elixir (and therefore SQLAlchemy) to
interface with the database. Makes certain assumptions about project layout
and uses those assumptions to take action.

Assumptions
===========

* Routes are set up with map.resource like this:

  map.resource('member_name', 'collection_name')

  Example:
      map.resource('cow', 'cows')

* Nested resource routes are set up like this:

  map.resource('member_name', 'collection_name',
               path_prefix='parent_collection_name/:parent_id')

  Note that you must use :parent_id and not any other name. Replace
  parent_collection_name with the plural name of your parent resource.

  Example:
      map.resource('animal', 'animals')
      map.resource('cow', 'cows', path_prefix='animals/:parent_id'))

* lib.base imports your model under the name ``model`` and your model will...
  * connect to your database via SQLAlchemy,
  * contain a function named ``connectMetadata`` that binds elixir.metadata to
    your database engine,
  * expose your elixir.Entity classes, regardless of where they are
    actually defined.

* Templates for a resource are in project/templates/collection_name.

  Template file names correspond to controller action names, so there should
  be new, show, edit, and index templates.

  The default is to render templates with an HTML extension. If ``format`` is
  supplied to an action, that format will override the default.

  There are built-in methods to return HTML, HTML fragment, plain text, and
  JSON content. All except the last use templates with a corresponding
  extenstion (.html, .frag or .fragment, .text or .txt); JSON is rendered by
  calling the __simplify__ method of either the Entity objects of a collection
  or a single member/Entity object (depending on which action was invoked).

  [Possible FIXME: Should the Entity classes define a to_json method instead?
   But then that means they needs to know about JSON... which they are already
   sort-of aware of via their __simplify__ method.]

* Your controllers will inherit from RestController instead of BaseController:

  This module is a drop in replacement for lib.base, so do this in your
  controllers (which will pull in everything that's defined or imported in
  lib.base; you don't need to modify lib.base except to import you model):

    from tripplanner.lib.rest import *

  instead of this:

    from tripplanner.lib.base import *

"""
import simplejson
from pylons.util import class_name_from_module_name
from tripplanner.lib.base import *


class RestController(BaseController):
    """Base class for RESTful controllers."""

    def __init__(self):
        """Set up RESTful Controller.

        We assume the controller file is named after the resource's collection
        name and that there is a corresponding top level template directory.
        For example, for a Hat resource, the controller file will be named
        hats.py and there will be a template directory at /templates/hats.

        """
        model.connectMetadata()

        route = request.environ['routes.route']
        route_info = request.environ['pylons.routes_dict']

        self.parent_id = route_info.get('parent_id', None)
        self.controller = route_info['controller']
        self.action = route_info['action']

        # Get parent name and parent Entity class for nested controller
        self.parent_name = getattr(self, 'parent_name', None)
        if self.parent_name is not None:
            parent_entity_name = class_name_from_module_name(self.parent_name)
            self.ParentEntity = getattr(model, parent_entity_name)
        else:
            self.parent_name = 'parent'
            parent_entity_name = None
            self.ParentEntity = None

        # The collection name should be the same as the controller's file name
        self.collection_name = route.collection_name
        assert self.collection_name == self.controller
        self.member_name = route.member_name

        entity_name = class_name_from_module_name(self.member_name)

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
        self._set_collection_by_id(parent_id)
        return self._render_response(format)

    def new(self, parent_id=None, format=None):
        """GET /resource/new

        Show a form for creating a new item. The form should POST to
        /resource/create.

        ``parent_id``
            If given, the new item's parent will be the object of the
            ``ParentEntity`` class having that ID.

        """
        self._set_member_by_id(parent_id)
        return self._render_response(format)

    def show(self, parent_id=None, id=None, format=None):
        """GET /resource/id

        Show existing item that has parent ID ``parent_id`` and ID ``id``.

        """
        self._set_member_by_id(parent_id, id)
        return self._render_response(format)

    def edit(self, parent_id=None, id=None, format=None):
        """GET /resource/id;edit

        Show a form for editing an existing item that has parent ID
        ``parent_id`` and ID ``id``. The form should PUT to /resource/update.

        """
        self._set_member_by_id(parent_id, id)
        return self._render_response(format)

    def create(self, parent_id=None, format=None):
        """POST /resource

        Create with POST data a new item that has parent ID ``parent_id``.

        """
        self._set_member_by_id(parent_id)

        # TODO: Add POST data to self.member here.

        self.Entity.flush([self.member])
        redirect_to(id=self.member.id, parent_id=parent_id, format=format,
                    action='show')

    def update(self, parent_id=None, id=None, format=None):
        """PUT /resource/id

        Update with PUT data an existing item that has parent ID ``parent_id``
        and ID ``id`` .

        """
        self._set_member_by_id(parent_id, id)

        # TODO: Update self.member with PUT data here.

        self.Entity.flush([self.member])
        redirect_to(parent_id=parent_id, id=id, format=format, action='show')

    def delete(self, parent_id=None, id=None, format=None):
        """DELETE /resource/id

        Delete the existing item that has parent_id ``parent_id`` ID ``id``.

        """
        self._set_member_by_id(parent_id, id)
        self.Entity.delete(self.member)
        self.Entity.flush([self.member])
        redirect_to(parent_id=parent_id, format=format, action='index')

    def _setattr(self, name, value):
        """Set attribute on both ``c`` and ``self``.

        ``name``
            The name of the attribute (the specific resource name)

        ``value``
            The value of the attribute

        """
        setattr(self, name, value)
        setattr(c, name, value)

    def _get_parent(self):
        return self._parent
    def _set_parent(self, parent):
        """Set the parent object to ``parent``."""
        self._parent = parent
        # 'parent' is the default parent name. If we don't check for this
        # we'll end up in a nice recursively infinite loop when calling
        # _setattr.
        if self.parent_name != 'parent':
            self._setattr(self.parent_name, parent)
        else:
            c.parent = parent
    parent = property(_get_parent, _set_parent)

    def _get_member(self):
        return self._member
    def _set_member(self, member):
        """Set the member object to ``member``."""
        self._member = member
        self._setattr(self.member_name, member)
    member = property(_get_member, _set_member)

    def _get_collection(self):
        return self._collection
    def _set_collection(self, collection):
        """Set the collection object to ``collection``."""
        self._collection = collection
        self._setattr(self.collection_name, collection)
    collection = property(_get_collection, _set_collection)

    def _set_parent_by_id(self, parent_id=None):
        """Set parent attribute on both ``self`` and ``c``.

        The member is attached as parent_name, where parent_name is specified
        in the child controller (defaults to "parent").

        """
        if self.ParentEntity and parent_id is not None:
            self.parent = self.ParentEntity.get(parent_id)
        else:
            self.parent = None

    def _set_member_by_id(self, parent_id=None, id=None):
        """Set member attribute on both ``self`` and ``c``.

        The member is attached as member_name, where member_name is the
        singular form of the resource.

        ``parent_id``
            The ID of the parent resource, if this is a nested resource

        ``id``
            The ID of the member to attach

        """
        self._set_parent_by_id(parent_id)
        self.member = self.Entity.get(id) if id is not None else self.Entity()

    def _set_collection_by_id(self, parent_id=None, page=0, num_items=10):
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
        self._set_parent_by_id(parent_id)
        self.collection = self.Entity.select()

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

        c.wrap = self._wrap()

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

    def _get_xml_content(self):
        """Get XML content."""
        html = render('%s.xml' % self.template)
        return html, 'text/xml'

    def _wrap(self):
        """Whether to wrap a template in its parent template.

        Default is `True`. If wrap is set in query params, convert its value
        to bool and use that value; otherwise, return True.

        """
        wrap = request.params.get('wrap', 'true')
        if wrap.lower() in ('0', 'n', 'no', 'false', 'nil'):
            return False
        return True
