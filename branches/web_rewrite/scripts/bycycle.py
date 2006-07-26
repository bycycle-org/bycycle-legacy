#!/home/bycycle/bin/python
"""Command-line interface to the byCycle library."""
import sys
import getopt
from byCycle.tripplanner.model import regions


import_path = 'byCycle.tripplanner.services.%s'

services = {
    'n': 'normaddr',
    'g': 'geocode',
    'r': 'route'
    }

errors = []
            
    
def main():
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], '')
    except getopt.GetoptError:
        addError('Unkown option(s) specified')

    checkForErrors()

    try:
        service = args[0]
    except IndexError:
        addError('No service specified')
    else:
        if service in services:
            service = services[service]
        try:
            service_module = __import__(import_path % service,
                                        globals(), locals(), [''])
        except ImportError:
            addError('Unknown service "%s"' % service)
        
    try:
        q = args[1]
    except IndexError:
        addError('No query specified')

    checkForErrors()

    if service == 'route':
        if len(q.lower().split(' to ')) < 2:
            addError('Route must be specified as "A to B"')
        else:
            q = q.split(' to ')

    checkForErrors()

    try:
        region = args[2]
    except IndexError:
        region = ''

    region = regions.getRegion(region)
    response = service_module.get(q=q, region=region)
    print response


def addError(e):
    errors.append(e)


def checkForErrors():
    if errors:
        usage(errors)
        sys.exit(2)

        
def usage(msgs=[]):
    print 'Usage: bycycle.py ' \
          '<normaddr|n|geocode|g|route|r> ' \
          '<query|address|intersection> ' \
          '[<region>]'
    for msg in msgs:
        print '- %s' % msg


if __name__ == '__main__':
    main()
    
