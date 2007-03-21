"""

Adds support for Rails-style RESTful ActiveRecord resources. Provides a
RESTful controller class that uses Elixir (and therefore SQLAlchemy) to
interface with the database. Makes certain assumptions about project layout
and uses those assumptions to take action.

Assumptions
===========

* Routes are set up with ``map.resource`` like this:

  map.resource(<member_name>, <collection_name>)

  Example::

      >>> from routes import *
      >>> m = Mapper()
      >>> m.resource('cow', 'cows')
      >>> url_for('cow', id='bessy')
      '/cows/bessy'
      >>> url_for('new_cow')
      '/cows/new'
      >>> url_for('cows')
      '/cows'

* Nested resource routes are set up like this:

  map.resource(<member_name>, <collection_name>,
               parent_resource={'collection_name': <parent_collection_name>,
                                'member_name': <parent_member_name>})

  Example::

      >>> m = Mapper()
      >>> m.resource('cow', 'cows',
      ...            parent_resource={'collection_name': 'farmers',
      ...                             'member_name': 'farmer'})
      >>> url_for('farmer_cow', farmer_id='bob', id='bessy')
      '/farmers/bob/cows/bessy'
      >>> url_for('farmer_new_cow', farmer_id='bob')
      '/farmers/bob/cows/new'
      >>> url_for('farmer_cows', farmer_id='bob')
      '/farmers/bob/cows'

* lib.base imports your model under the name ``model`` and your model will...
  * connect to your database via SQLAlchemy,
  * contain a function named ``connectMetadata`` that binds elixir.metadata to
    your database engine,

    >>> from base import *
    >>> model.connectMetadata  # doctest: +ELLIPSIS
    <function connectMetadata at ...>

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
  lib.base; you don't need to modify lib.base except possibly to import your
  model):

      from <yourproject>.lib.rest import *

  instead of this:

      from <yourproject>.lib.base import *

"""
import simplejson
from pylons.util import class_name_from_module_name
from base import *
from base import __all__ as __base_all__


__all__ = __base_all__ + ['RestController']


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

        self.parent_resource = route.parent_resource
        self.controller = route_info['controller']
        self.action = route_info['action']

        name = getattr(self, 'parent_member_name', None)
        if name is None and self.parent_resource is not None:
            name = self.parent_resource['member_name']
        self.parent_member_name = name
        self.parent_id_name = '%s_id' % name
        self.parent_id = route_info.get(self.parent_id_name, None)

        name = getattr(self, 'parent_collection_name', None)
        if name is None and self.parent_resource is not None:
            name = self.parent_resource['collection_name']
        self.parent_collection_name = name

        # Get parent Entity class for nested controller
        if self.parent_member_name is not None:
            f = class_name_from_module_name
            self.parent_entity_name = f(self.parent_member_name)
            self.ParentEntity = getattr(model, self.parent_entity_name)
        else:
            self.parent_entity_name, self.ParentEntity = None, None

        self.collection_name = (getattr(self, 'collection_name', None) or
                                route.collection_name)
        self.member_name = (getattr(self, 'member_name', None) or
                            route.member_name)

        self.entity_name = class_name_from_module_name(self.member_name)

        # Import the entity class for the resource
        self.Entity = getattr(model, self.entity_name)

    def index(self, format=None):
        """GET /

        Show all (or subset of) items in collection.

        """
        self._set_collection_by_id()
        return self._render_response(format)

    def new(self, format=None):
        """GET /resource/new

        Show a form for creating a new item. The form should POST to
        /resource/create.

        """
        self._set_member_by_id()
        return self._render_response(format)

    def show(self, id=None, format=None):
        """GET /resource/id

        Show existing item that has ID ``id``.

        """
        self._set_member_by_id(id)
        return self._render_response(format)

    def edit(self, id=None, format=None):
        """GET /resource/id;edit

        Show a form for editing an existing item that has ID ``id``. The form
        should PUT to /resource/update.

        """
        self._set_member_by_id(id)
        return self._render_response(format)

    def create(self, format=None):
        """POST /resource

        Create with POST data a new item.

        """
        self._set_member_by_id()

        # TODO: Add POST data to self.member here.

        self.Entity.flush([self.member])
        args = {'id': self.member.id, self.parent_id_name: self.parent_id,
                'format': format, 'action': 'show'}
        redirect_to(**args)

    def update(self, id=None, format=None):
        """PUT /resource/id

        Update with PUT data an existing item that has ID ``id`` .

        """
        self._set_member_by_id(id)

        # TODO: Update self.member with PUT data here.

        self.Entity.flush([self.member])
        args = {'id': id, self.parent_id_name: self.parent_id,
                'format': format, 'action': 'show'}
        redirect_to(**args)

    def delete(self, id=None, format=None):
        """DELETE /resource/id

        Delete the existing item that has ID ``id``.

        """
        self._set_member_by_id(id)
        self.Entity.delete(self.member)
        self.Entity.flush([self.member])
        args = {self.parent_id_name: self.parent_id, 'format': format,
                'action': 'show'}
        redirect_to(**args)

    def __setattr__(self, name, value):
        """Set attribute on both ``c`` and ``self``."""
        if isinstance(getattr(self.__class__, name, None), property):
            super(RestController, self).__setattr__(name, value)
        else:
            self.__dict__[name] = value
        setattr(c, name, value)

    def _get_parent(self):
        return getattr(self, self.parent_member_name, None)
    def _set_parent(self, parent):
        self.__dict__['parent'] = parent
        setattr(self, self.parent_member_name, parent)
    parent = property(_get_parent, _set_parent)

    def _get_parent_id(self):
        return getattr(self, self.parent_id_name, None)
    def _set_parent_id(self, parent_id):
        self.__dict__['parent_id'] = parent_id
        setattr(self, self.parent_id_name, parent_id)
    parent_id = property(_get_parent_id, _set_parent_id)

    def _get_collection(self):
        return getattr(self, self.collection_name, None)
    def _set_collection(self, collection):
        self.__dict__['collection'] = collection
        setattr(self, self.collection_name, collection)
    collection = property(_get_collection, _set_collection)

    def _get_member(self):
        return getattr(self, self.member_name, None)
    def _set_member(self, member):
        self.__dict__['member'] = member
        setattr(self, self.member_name, member)
    member = property(_get_member, _set_member)

    def _set_parent_by_id(self, parent_id=None):
        if parent_id is None:
            parent_id = self.parent_id
        if parent_id is not None and self.ParentEntity:
            self.parent = self.ParentEntity.get(parent_id)

    def _set_member_by_id(self, id=None, parent_id=None):
        self._set_parent_by_id(parent_id)
        if id is not None:
            entity = self.Entity.get(id)
        else:
            entity = self.Entity()
        setattr(self, self.member_name, entity)

    def _set_collection_by_id(self, parent_id=None, page=0, num_items=10):
        self._set_parent_by_id(parent_id)
        setattr(self, self.collection_name, self.Entity.select())

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

    def _get_json_content(self, block=None):
        """Get a JSON string and mimetype "text/javascript".

        Assumes members have a __simplify__ method that returns an object
        that can be JSONified by the simplejson module. That object is
        JSONified and returned unless the ``obj_fun`` arg is supplied.

        ``block``
            This method creates the simplest possible object to be JSONified
            (``obj``) by calling __simplify__ on a member or members. If a
            function is passed via ``block``, that function will be called
            with ``obj``, and ``obj`` can be modified there before being
            JSONified here.

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
        if block is not None:
            obj = block(obj)
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
