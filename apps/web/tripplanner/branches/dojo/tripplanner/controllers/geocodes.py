from byCycle.services.geocode import Service, MultipleMatchingAddressesError

from tripplanner.lib.base import *
from tripplanner.controllers.services import ServicesController


class GeocodesController(ServicesController):
    """Controller for interfacing with byCycle Geocode service."""

    def find(self, region_id):
        q = request.params.get('q', None)
        c.q = q
        try:
            return super(GeocodeController, self).show(
                query, region, service_class=Service
            )
        except MultipleMatchingAddressesError, exc:
            self.template = 'geocodes'
            self.results = exc.geocodes
            self.http_status = 300
            c.title = 'Multiple Matches Found'
            c.classes = 'errors'
        # We'll get here only if there's an unhandled error in the superclass.
        # Otherwise, the superclass will handle rendering directly.
        return self._render_response()
