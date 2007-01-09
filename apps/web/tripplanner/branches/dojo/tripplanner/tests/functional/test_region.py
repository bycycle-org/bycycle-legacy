from tripplanner.tests import *

class TestRegionController(TestController):
    def test_index(self):
        response = self.app.get(url_for(controller='region'))
        # Test response...