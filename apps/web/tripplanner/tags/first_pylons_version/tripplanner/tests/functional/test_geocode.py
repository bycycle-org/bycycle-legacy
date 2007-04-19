from tripplanner.tests import *

class TestGeocodeController(TestController):
    def test_index(self):
        response = self.app.get(url_for(controller='geocode'))
        # Test response...