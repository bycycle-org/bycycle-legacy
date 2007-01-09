from tripplanner.tests import *

class TestRouteController(TestController):
    def test_index(self):
        response = self.app.get(url_for(controller='route'))
        # Test response...