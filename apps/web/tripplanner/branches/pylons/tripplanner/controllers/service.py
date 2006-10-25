import time
import simplejson
from byCycle.services.exceptions import *
from tripplanner.lib.base import *
from tripplanner.controllers.rest import RestController


class ServiceController(RestController):
    """Base class for controllers that interact with back end services."""

    #----------------------------------------------------------------------
    def show(self, query, region, service_class=None):
        query = query or request.params.get('q', None)
        c.q = query
        format = request.params.get('format', 'html')
        service = service_class(region=region)
        result = None
        to_json = None
        try:
            result = service.query(query)
        except InputError, exc:
            c.title = 'Bad Input'
            http_status = 400
        except NotFoundError, exc:
            c.title = 'Not Found'
            http_status = 404
        except ByCycleError:
            # Let subclass deal with any other `ByCycleError`s
            self.service = service
            self.format = format
            raise
        except Exception, exc:
            c.title = 'Error'
            exc.description = str(exc)
            http_status = 500
        else:
            template = service.name
            http_status = 200
            c.title = service.name.title()
            to_json = eval(repr(result))

        try:
            # Was there an error?
            exc
        except UnboundLocalError:
            pass
        else:
            template = 'error'
            c.classes = 'errors'
            c.error_msg = exc.description

        return self._render(
            service, template, http_status, format, result, to_json
        )

    #----------------------------------------------------------------------
    def _render(self, service, template, http_status=200, format='html',
                oResult=None, to_json=None):
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

        ``to_json`` `str` -- A Python object that can be JSONififed.

        return `WSGIResponse`

        """
        # Used by all formats
        json = simplejson.dumps(to_json)
        # Used by frag and html
        result_template = '/service/%s.myt' % template
        c.service = service
        c.result_id = ('%.6f' % time.time()).replace('.', '')
        c.json = json
        if format == 'json':
            resp = Response(
                content=json, mimetype='text/plain', code=http_status
            )
        else:
            content = render(result_template, oResult=oResult)
            if format.startswith('frag'):
                resp = Response(
                    content=content,
                    code=http_status
                )
            else:
                from tripplanner.controllers.region import RegionController
                if http_status == 200:
                    c.result = content
                else:
                    c.errors = content
                c.info = '\n'
                c.help = None
                controller = RegionController()
                resp = controller.show(service.region.key, service.name)
                resp.status_code = http_status
        return resp
