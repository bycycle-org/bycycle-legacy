from tripplanner.tests import *

class TestQueryController(TestController):
    def test_index(self):
        response = self.app.get(url_for(controller='query'))
        # Test response...