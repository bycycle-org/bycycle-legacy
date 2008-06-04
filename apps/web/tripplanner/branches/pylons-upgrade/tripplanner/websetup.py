"""Setup the tripplanner application"""
from paste.deploy import appconfig

from pylons import config

from byCycle import model

from tripplanner.config.environment import load_environment

def setup_config(command, filename, section, vars):
    """Place any commands to setup tripplanner here"""
    print '== Setting up byCycle Trip Planner Web application...'
    conf = appconfig('config:' + filename)
    load_environment(conf.global_conf, conf.local_conf)
    print '== Done setting up byCycle Trip Planner Web application.'
