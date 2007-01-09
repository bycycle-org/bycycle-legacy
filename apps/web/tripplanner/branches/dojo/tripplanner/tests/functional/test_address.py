from tripplanner.tests import *

class TestAddressController(TestController):
    def test_index(self):
        response = self.app.get(url_for(controller='address'))
        # Test response...