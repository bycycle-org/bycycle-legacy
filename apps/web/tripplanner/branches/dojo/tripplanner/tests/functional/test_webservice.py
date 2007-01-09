from tripplanner.tests import *

class TestWebserviceController(TestController):
    def test_index(self):
        response = self.app.get(url_for(controller='webservice'))
        # Test response...