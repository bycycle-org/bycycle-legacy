import sys, os
from routes import Mapper
def make_map():
    root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    map = Mapper(directory=os.path.join(root_path, 'controllers'))
    map.connect('home', '', controller='root', action='index')
    map.connect(':region', controller='root', action='region')
    map.connect(':service/:query', controller='root', action='service')
    map.connect(':region/:service/:query', controller='root', 
                action='service')
    map.connect('*url', controller='template', action='view')
    return map
  
