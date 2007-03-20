#!/usr/bin/env python
"""Create adjacency matrix for region given as first arg on command line."""
import sys
from byCycle.model import regions

no_region_msg = ('Specify a region name. Use "all" to create matrices for '
                 'all regions.')

def die(error_msg):
    sys.stderr.write(str(error_msg) + '\n')
    sys.exit(1)

region_key = sys.argv[1] if len(sys.argv) > 1 else die(no_region_msg)

def make_matrix_for_region(region_key):
    try:
        region = regions.getRegion(region_key)
    except ValueError, e:
        die('Unknown region: %s.' % region_key)
    else:
        print 'Creating matrix for %s...' % region.title
        region.createAdjacencyMatrix()

if region_key == 'all':
    print 'Creating all matrices...'
    for key in regions.region_keys:
        make_matrix_for_region(key)
else:
    make_matrix_for_region(region_key)

