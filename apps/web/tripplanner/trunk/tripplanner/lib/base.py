from pylons import config, request, g, session
from pylons import tmpl_context as c
from pylons.controllers import WSGIController
from pylons.controllers.util import abort, redirect_to
from pylons.decorators import validate, jsonify
from pylons.templating import render_mako as render

import restler

from byCycle import model

import tripplanner.lib.helpers as h


class RestController(restler.RestController(model)):
    def __call__(self, *args, **kwargs):
        c.wrap = True
        return WSGIController.__call__(self, *args, **kwargs)


class BaseController(WSGIController):
    pass

