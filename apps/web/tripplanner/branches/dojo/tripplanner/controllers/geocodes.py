from byCycle.services.geocode import Service, MultipleMatchingAddressesError

from tripplanner.controllers.services import *


class GeocodesController(ServicesController):
    """Controller for interfacing with byCycle Geocode service."""

    def find(self):
        q = request.params.get('q', '')
        c.q = q
        try:
            return super(GeocodesController, self)._find(
                q, service_class=Service
            )
        except MultipleMatchingAddressesError, exc:
            template = '300'
            c.http_status = 300
            self.collection = exc.geocodes
        # We'll get here only if there's an unhandled error in the superclass.
        # Otherwise, the superclass will handle rendering.
        return self._render_response(
            format=self.format, template=template, code=c.http_status
        )
