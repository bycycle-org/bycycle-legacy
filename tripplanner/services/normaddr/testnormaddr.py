if __name__ == '__main__':
    import unittest
    from byCycle.tripplanner.services.normaddr import *
    from byCycle.tripplanner.model import *
    from byCycle.tripplanner.model import portlandor


    class TestGetCrossStreets(unittest.TestCase):
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
        

    class TestNormAddrPortlandOR(unittest.TestCase):
        def setUp(self):
            try:
                self.mode
            except AttributeError:
                self.mode = portlandor.Mode() 
        
        def testPortlandORPostalAddress(self): 
            sAddr = '4807 SE Kelly St, Portland, OR 97206'
            oAddr = get(sAddr, self.mode)
            self.assert_(isinstance(oAddr, address.PostalAddress))
            
        def testPortlandOREdgeAddress(self):
            Q = 'SELECT id FROM portlandor_layer_street ' \
                'WHERE addr_f <= 633 AND addr_t >= 633 AND ' \
                'streetname_id IN ' \
                '(SELECT id from portlandor_streetname ' \
                ' WHERE prefix = "n" AND name = "alberta" AND type = "st")'
            self.mode.execute(Q)
            edge_id = self.mode.fetchRow()[0]
            sAddr = '4807 %s' % edge_id
            oAddr = get(sAddr, self.mode)
            self.assert_(isinstance(oAddr, address.EdgeAddress))
            self.assert_(isinstance(oAddr, address.PostalAddress))
            
        def testPortlandORIntersectionAddress(self):
            sAddr = 'SE Kelly St & SE 49th Ave, Portland, OR 97206'
            oAddr = get(sAddr, self.mode)
            self.assert_(isinstance(oAddr, address.IntersectionAddress))

        def testPortlandORPointAddress(self):
            sAddr = 'POINT(-123.120000 45.000000)'
            oAddr = get(sAddr, self.mode)
            self.assert_(isinstance(oAddr, address.PointAddress))
            self.assert_(isinstance(oAddr, address.IntersectionAddress))

        def testPortlandORNodeAddress(self):
            sAddr = '4'
            oAddr = get(sAddr, self.mode)
            self.assert_(isinstance(oAddr, address.IntersectionAddress))

            
    unittest.main()
    
