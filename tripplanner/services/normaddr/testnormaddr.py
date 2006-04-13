if __name__ == '__main__':
    import unittest
    from byCycle.tripplanner.services.normaddr import *
    from byCycle.tripplanner.model import portlandor


    class TestgetCrossStreets(unittest.TestCase):
        def _testGood(self, addrs):
            for addr in addrs:
                streets = getCrossStreets(addr)
                self.assertEqual(len(streets), 2)        
        
        def _testBad(self, addrs):
            for addr in addrs:
                self.assertRaises(ValueError, getCrossStreets, addr)
                
        def testAnd(self):
            addrs = ('A and B', 'A And B', 'A aNd B', 'A anD B', 'A AND B')
            self._testGood(addrs)

        def testAt(self):
            addrs = ('A at B', 'A At B', 'A aT B', 'A AT B')
            self._testGood(addrs)
            
        def testAtSymbol(self):
            addrs = ('A @ B', 'A @B', 'A@ B', 'A@B')
            self._testGood(addrs)
            
        def testForwardSlash(self):
            addrs = ('A / B', 'A /B', 'A/ B', 'A/B')
            self._testGood(addrs)
            
        def testBackSlash(self):
            addrs = (r'A \ B', r'A \B', r'A\ B', r'A\B')
            self._testGood(addrs)
            
        def testPlus(self):
            addrs = ('A + B', 'A +B', 'A+ B', 'A+B')
            self._testGood(addrs)

        def testMissingInternalSpace(self):
            addrs = ('A andB', 'Aat B')
            self._testBad(addrs)

        def testMissingFromOrTo(self):
            addrs = ('and B', 'A at', ' and B', 'A at ')
            self._testBad(addrs)

        def testMissingFromAndTo(self):
            addrs = ('and', ' and', 'and ', ' and ')
            self._testBad(addrs)
            

    class TestGetNumberAndStreet(unittest.TestCase):
        def _testGood(self, addrs):
            for addr in addrs:
                num, street = getNumberAndStreet(addr)
                self.assertEqual(type(num), int)
                self.assertEqual(type(street), str)
        
        def _testBad(self, addrs):
            for addr in addrs:
                self.assertRaises(ValueError, getNumberAndStreet, addr)

        def testGood(self):
            addrs = ('633 Alberta', '633 N Alberta', '633 N Alberta St',
                     '633 N Alberta St Portland',
                     '633 N Alberta St, Portland',
                     '633 N Alberta St, Portland, OR 97217',)
            self._testGood(addrs)

        def testBad(self):
            addrs = ('633', 'Alberta & Kerby', 'x=-123, y=45')
            self._testBad(addrs)
        

    class TestNormAddr:
        def testPortlandORPostalAddress(self): 
            mode = portlandor.Mode()
            inaddr = '4807 SE Kelly St, Portland, OR 97206'
            self.assert_(isinstance(get(inaddr, mode),
                                    address.AddressAddress))

        def testPortlandORIntersectionAddress(self):
            inaddr = 'SE Kelly St & SE 49th Ave, Portland, OR 97206'
            mode = portlandor.Mode()
            self.assert_(isinstance(get(inaddr, mode),
                                    address.IntersectionAddress))

        def testPortlandORPointAddress(self):
            inaddr = 'POINT(-123.120000 45.000000)'
            mode = portlandor.Mode()
            self.assert_(isinstance(get(inaddr, mode), address.PointAddress))
            self.assert_(isinstance(get(inaddr, mode),
                                    address.IntersectionAddress))

        def testPortlandORNodeAddress(self):
            inaddr = '4'
            mode = portlandor.Mode()
            self.assert_(isinstance(get(inaddr, mode),
                                    address.IntersectionAddress))

        def testPortlandOREdgeAddress(self):
            mode = portlandor.Mode()
            Q = 'SELECT id FROM portlandor_layer_street ' \
                'WHERE addr_f <= 4807 AND addr_t >= 4807 AND ' \
                'streetname_id IN ' \
                '(SELECT id from portlandor_streetname ' \
                ' WHERE prefix = "se" AND name = "kelly" AND type = "st")'
            mode.execute(Q)
            edge_id = mode.fetchRow()[0]
            inaddr = '4807 %s' % edge_id
            self.assert_(isinstance(get(inaddr, mode), address.AddressAddress))

            
    unittest.main()
    
