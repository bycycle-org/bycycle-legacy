import cgi
import os.path

from paste.urlparser import StaticURLParser
from pylons.middleware import error_document_template, media_path
from pylons import request
from pylons import tmpl_context as c
from pylons.templating import render_mako as render

from mako.exceptions import TopLevelLookupException

from webhelpers.html.builder import literal

from bycycle.tripplanner.lib.base import BaseController


class ErrorController(BaseController):
    """Generates error documents as and when they are required.

    The ErrorDocuments middleware forwards to ErrorController when error
    related status codes are returned from the application.

    This behaviour can be altered by changing the parameters to the
    ErrorDocuments middleware in your config/middleware.py file.

    """
    def document(self):
        """Render the error document"""
        req = request.environ.get('pylons.original_request')
        resp = request.environ.get('pylons.original_response')
        code, reason = resp.status.split(' ', 1)
        try:
            path, format = req.path_info.strip('/').rsplit('.', 1)
        except ValueError, e:
            format = 'html'
        try:
            return render('/error/%s.%s' % (code, format))
        except TopLevelLookupException:
            content = (
                literal(resp.body) or cgi.escape(request.GET.get('message')))
            page = error_document_template % (
                dict(prefix=request.environ.get('SCRIPT_NAME', ''),
                     code=cgi.escape(request.GET.get('code', resp.status)),
                     message=content))
            return page

    def img(self, id):
        """Serve Pylons' stock images"""
        return self._serve_file(os.path.join(media_path, 'img'), id)

    def style(self, id):
        """Serve Pylons' stock stylesheets"""
        return self._serve_file(os.path.join(media_path, 'style'), id)

    def _serve_file(self, root, path):
        """Call Paste's FileApp (a WSGI application) to serve the file
        at the specified path
        """
        static = StaticURLParser(root)
        request.environ['PATH_INFO'] = '/%s' % path
        return static(request.environ, self.start_response)
