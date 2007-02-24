import paste.deploy
from byCycle import model


def setup_config(command, filename, section, vars):
    """Set up the application."""
    print '== Setting up byCycle Trip Planner Web application...'
    
    # Get configuration
    conf = paste.deploy.appconfig('config:' + filename)
    app_conf = conf.local_conf
    paste.deploy.CONFIG.push_process_config({
        'app_conf': app_conf,
        'global_conf': conf.global_conf
    })

    # Create database tables that don't exist
    print '== Creating database tables (only those that do not exist)...'
    #model.drop_all()
    model.create_all()
    print '== Done creating database tables.'

    print '== Done setting up byCycle Trip Planner Web application.'
