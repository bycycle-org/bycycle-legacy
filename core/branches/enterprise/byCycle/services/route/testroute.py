################################################################################
# $Id: testgeocode.py 208 2006-09-11 03:41:35Z bycycle $
# Created 2006-09-25.
#
# Unit tests for route service.
#
# Copyright (C) 2006 Wyatt Baldwin, byCycle.org <wyatt@bycycle.org>.
# All rights reserved.
#
# For terms of use and warranty details, please see the LICENSE file included
# in the top level of this distribution. This software is provided AS IS with
# NO WARRANTY OF ANY KIND.
################################################################################
import unittest
from byCycle.util import meter
from byCycle.services.route import *
from byCycle.model.route import Route


timer = meter.Timer()


class TestPortlandOR(unittest.TestCase):

    def _query(self, q, region=None):
        print '=========='
        timer.start()
        service = Service(region=region)
        routes = service.query(q)
        route = routes[0]
        self.assert_(isinstance(route, Route))
        print route
        print 'Took %.2f seconds' % timer.stop()
        print '=========='
        return route

    def _queryRaises(self, q, exc):
        self.assertRaises(exc, self._query, q)

    def _test_no_place_on_first_address(self):
        q = ('4807 se kelly', '633 n alberta, portland, or')
        route = self._query(q)

    def _test_no_place_on_second_address(self):
        q = ('4807 se kelly, portland, or', '633 n alberta')
        route = self._query(q)

    def test_route(self):
        q = ('4807 se kelly, portland, or', '45th and division, portland, or')
        #route = self._query(q)
        #q = ('250 ne going, portland, or', '350 n going, portland, or')
        #q = ('634 beech portland or','633 n alberta, portland or')
        try:
            route = self._query(q)
        except MultipleMatchingAddressesError, exc:
            print exc.choices

    def _test_three_addresses(self):
        q = ('4807 se kelly, portland, or', '633 n alberta', '1500 ne alberta')
        route = self._query(q)


if __name__ == '__main__':
    unittest.main()


"""
if __name__ == '__main__':
    import sys


    def print_key(key):
        for k in key:
            print k,
            if type(key[k]) == type({}):
                print
                for l in key[k]:
                    print '\t', l, key[k][l]
            else: print key[k]
        print

    try:
        region, q = sys.argv[1].split(',')
    except IndexError:
        Qs = {'milwaukeewi':
              (('Puetz Rd & 51st St', '841 N Broadway St'),
               ('27th and lisbon', '35th and w north'),
               ('S 84th Street & Greenfield Ave',
                'S 84th street & Lincoln Ave'),
               ('3150 lisbon', 'walnut & n 16th '),
               ('124th and county line, franklin', '3150 lisbon'),
               ('124th and county line, franklin',
                'x=-87.940407, y=43.05321'),
               ('x=-87.973645, y=43.039615',
                'x=-87.978623, y=43.036086'),
               ),
              'portlandor':
               (('x=-122.668104, y=45.523127', '4807 se kelly'),
                ('x=-122.67334,y=45.621662', '8220 N Denver Ave'),
                ('633 n alberta', '4807 se kelly'),
                ('sw hall & denney', '44th and se stark'),
                ('-122.645488, 45.509475', 'sw hall & denney'),
               ),
              }
    else:
        q = q.split(' to ')
        Qs = {region: (q,)}


    for region in ['portlandor']:
        service = Service(region=region)
        qs = Qs[region]
        for q in qs:
            try:
                timer.start()
                r = service.query(q)
            except MultipleMatchingAddressesError, e:
                print e.route
            except NoRouteError, e:
                print e
            #except Exception, e:
            #    print e
            else:
                D = r['directions']
                print r['start']['geocode']
                print r['end']['geocode']
                for d in D:
                    print '%s on %s toward %s -- %s mi [%s]' % \
                          (d['turn'],
                           d['street'],
                           d['toward'],
                           d['distance']['mi'],
                           d['bikemode'])
                print
                print 'Took %.2f' % timer.stop()
                print '----------------------------------------' \
                      '----------------------------------------'
"""
