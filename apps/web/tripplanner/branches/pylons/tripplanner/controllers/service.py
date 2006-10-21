import time
from tripplanner.lib.base import *
from tripplanner.controllers.rest import RestController


class ServiceController(RestController):
    """Base class for controllers that interact with back end services."""

    def _render(self, service, template, http_status=200, format='html',
                json=None):
        """Render response after query to service.

        Branch according to ``format`` and return the appropriate type of
        response. ``format`` may be one of "frag" (or "fragment"), "json", or
        "html" (default). "frag" will return an HTML fragment that will
        replace the result area of the currently displayed page. "json" will
        return a JSON object. "html" will return a complete HTML template with
        the result filled in.

        ``service`` `Service` -- A back end service object.

        ``template`` `str` -- Name of template to render.

        ``http_status`` `int` -- HTTP status code.

        ``format`` `str` -- Format for the response: HTML (full template),
        fragment (partial), or JSON.

        ``json`` `str` -- A JSON string that can be evaled into a JavaScript
        object.

        return `WSGIResponse`

        """
        c.service = service
        # Used by all formats
        c.json = json
        # Used by frag and html
        result_template = '/service/%s.myt' % template
        c.result_id = ('%.6f' % time.time()).replace('.', '')
        if format.startswith('frag'):
            return Response(
                content=render(result_template),
                code=http_status
            )
        elif format == 'json':
            return Response(content=json,
                            mimetype='text/plain',
                            code=http_status)
        else:
            from tripplanner.controllers.region import RegionController
            c.result = render(result_template)
            controller = RegionController()
            resp = controller.show(service.region.key, service.name)
            resp.status_code = http_status
            return resp
