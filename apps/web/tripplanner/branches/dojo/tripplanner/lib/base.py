from pylons import Response, c, g, cache, request, session
from pylons.controllers import WSGIController
from pylons.decorators import jsonify, validate
from pylons.templating import render, render_response
from pylons.helpers import abort, redirect_to, etag_cache
from pylons.i18n import N_, _, ungettext

from byCycle import model

import tripplanner.lib.helpers as h


class BaseController(WSGIController):
    def __call__(self, environ, start_response):
        return WSGIController.__call__(self, environ, start_response)


# This includes restler/base.py as if it contents had been written directly
# in this file.
execfile(__import__('restler').include_path)


# Include the '_' function in the public names
__all__ = [__name for __name in locals().keys() if not __name.startswith('_')
           or __name == '_']
