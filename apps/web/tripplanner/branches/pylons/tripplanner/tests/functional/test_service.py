from tripplanner.tests import *

class TestServiceController(TestController):
    def test_index(self):
        response = self.app.get(url_for(controller='service'))
        # Test response...