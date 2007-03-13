from os.path import abspath, dirname, join
import paste.deploy
base_path = dirname(abspath(__file__))
ini_name = 'production'
ini_path = join(base_path, '%s.ini' % ini_name)
config_uri = 'config:%s' % ini_path
wsgi_app = paste.deploy.loadapp(config_uri)
serve = paste.deploy.loadserver(config_uri)
serve(wsgi_app)

