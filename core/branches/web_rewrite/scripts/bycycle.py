#!/usr/bin/env python
"""$Id$

Command-line interface to the byCycle library.

Copyright (C) 2006 Wyatt Baldwin, byCycle.org <wyatt@bycycle.org>

All rights reserved.

TERMS AND CONDITIONS FOR USE, MODIFICATION, DISTRIBUTION

1. The software may be used and modified by individuals for noncommercial, 
private use.

2. The software may not be used for any commercial purpose.

3. The software may not be made available as a service to the public or within 
any organization.

4. The software may not be redistributed.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND 
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED 
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE 
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR 
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES 
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; 
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON 
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT 
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS 
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
import os
def __getbyCycleImportPath(level):
    """Get path to dir containing the byCycle package this module is part of.
    
    ``level`` `int`
        How many levels up the dir containing the package is.
    
    """
    path = os.path.abspath(__file__)
    opd = os.path.dirname
    for i in range(level):
        path = opd(path)
    return path

import sys
sys.path.insert(0, __getbyCycleImportPath(3))
from byCycle.model import regions

import_path = 'byCycle.services.%s'

services = {
    'n': 'normaddr',
    'g': 'geocode',
    'r': 'route'
    }

errors = []
    
def main(argv):
    checkForErrors()

    try:
        service = argv[1]
    except IndexError:
        addError('No service specified')
    else:
        if service in services:
            service = services[service]
        try:
            service_module = __import__(import_path % service,
                                        globals(), locals(), [''])
        except ImportError:
            raise
            addError('Unknown service "%s"' % service)
        
    try:
        q = argv[2]
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
        region = argv[3]
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
    main(sys.argv)
