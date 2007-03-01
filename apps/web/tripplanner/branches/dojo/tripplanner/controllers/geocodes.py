from byCycle.services.geocode import Service, MultipleMatchingAddressesError

from tripplanner.lib.base import *
from tripplanner.controllers.services import ServicesController


class GeocodesController(ServicesController):
    """Controller for interfacing with byCycle Geocode service."""

    def find(self, parent_id=None):
        q = request.params.get('q', '')

        try:
            return super(GeocodesController, self)._find(
                q, parent_id, service_class=Service
            )
        except MultipleMatchingAddressesError, exc:
            template = 'index'
            c.http_status = 300
            c.title = 'Multiple Matches Found'
            c.classes = 'errors'
            self._setattr(self.collection_name, exc.geocodes)

        # We'll get here only if there's an unhandled error in the superclass.
        # Otherwise, the superclass will handle rendering.
        return self._render_response(
            format=self.format, template=template, code=c.http_status
        )
