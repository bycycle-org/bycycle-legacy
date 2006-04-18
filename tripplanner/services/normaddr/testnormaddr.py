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
        def testPortlandORPostalAddress(self): 
            sAddr = '4807 SE Kelly St, Portland, OR 97206'
            sMode = 'portlandor'
            oAddr = get(sAddr, sMode)
            self.assert_(isinstance(oAddr, address.PostalAddress))
            self.assertEqual(oAddr.number, 4807)
            self.assertEqual(oAddr.prefix, 'se')
            self.assertEqual(oAddr.name, 'kelly')
            self.assertEqual(oAddr.sttype, 'st')
            self.assertEqual(oAddr.city, 'portland')
            self.assertEqual(oAddr.state_id, 'or')
            self.assertEqual(oAddr.zip_code, 97206)

        def testPortlandORPostalAddressMultiWordName(self): 
            sAddr = '4807 SE Martin Luther King Jr Boulevard, ' \
                    'Oregon City, OR 97206'
            sMode = 'portlandor'
            oAddr = get(sAddr, sMode)
            self.assert_(isinstance(oAddr, address.PostalAddress))
            self.assertEqual(oAddr.number, 4807)
            self.assertEqual(oAddr.prefix, 'se')
            self.assertEqual(oAddr.name, 'martin luther king jr')
            self.assertEqual(oAddr.sttype, 'blvd')
            self.assertEqual(oAddr.city, 'oregon city')
            self.assertEqual(oAddr.state_id, 'or')
            self.assertEqual(oAddr.zip_code, 97206)
            
        def testPortlandORPostalAddressMultiWordCity(self): 
            sAddr = '4807 SE Kelly St, Oregon City, OR 97206'
            sMode = 'portlandor'
            oAddr = get(sAddr, sMode)
            self.assert_(isinstance(oAddr, address.PostalAddress))
            self.assertEqual(oAddr.number, 4807)
            self.assertEqual(oAddr.prefix, 'se')
            self.assertEqual(oAddr.name, 'kelly')
            self.assertEqual(oAddr.sttype, 'st')
            self.assertEqual(oAddr.city, 'oregon city')
            self.assertEqual(oAddr.state_id, 'or')
            self.assertEqual(oAddr.zip_code, 97206)

        def testPortlandORPostalAddressMultiWordState(self): 
            sAddr = '4807 SE Kelly Pants St, Oregon City, South Dakota 97206'
            sMode = 'portlandor'
            oAddr = get(sAddr, sMode)
            self.assert_(isinstance(oAddr, address.PostalAddress))
            self.assertEqual(oAddr.number, 4807)
            self.assertEqual(oAddr.prefix, 'se')
            self.assertEqual(oAddr.name, 'kelly pants')
            self.assertEqual(oAddr.sttype, 'st')
            self.assertEqual(oAddr.city, 'oregon city')
            self.assertEqual(oAddr.state_id, 'sd')
            self.assertEqual(oAddr.zip_code, 97206)
            
        def testPortlandORPostalAddressNameEndsWithStreetType(self): 
            sAddr = '4807 SE Johnson Creek, ' \
                    'Oregon City, South Dakota 97206'
            sMode = 'portlandor'
            oAddr = get(sAddr, sMode)
            self.assert_(isinstance(oAddr, address.PostalAddress))
            self.assertEqual(oAddr.number, 4807)
            self.assertEqual(oAddr.prefix, 'se')
            self.assertEqual(oAddr.name, 'johnson creek')
            self.assertEqual(oAddr.sttype, '')
            self.assertEqual(oAddr.city, 'oregon city')
            self.assertEqual(oAddr.state_id, 'sd')
            self.assertEqual(oAddr.zip_code, 97206)
                    
        def testPortlandOREdgeAddress(self):
            Q = 'SELECT id FROM portlandor_layer_street ' \
                'WHERE addr_f <= 633 AND addr_t >= 633 AND ' \
                'streetname_id IN ' \
                '(SELECT id from portlandor_streetname ' \
                ' WHERE prefix = "n" AND name = "alberta" AND type = "st")'
            mode = portlandor.Mode()
            mode.execute(Q)
            edge_id = mode.fetchRow()[0]
            sAddr = '633 %s' % edge_id
            sMode = 'portlandor'
            oAddr = get(sAddr, sMode)
            self.assert_(isinstance(oAddr, address.EdgeAddress))
            self.assert_(isinstance(oAddr, address.PostalAddress))
            self.assertEqual(oAddr.number, 633)
            self.assertEqual(oAddr.edge_id, edge_id)
            
        def PortlandORIntersectionAddress(self):
            sAddr = 'SE Kelly St & SE 49th Ave, Portland, OR 97206'
            sMode = 'portlandor'
            oAddr = get(sAddr, sMode)
            self.assert_(isinstance(oAddr, address.IntersectionAddress))
            self.assertEqual(oAddr.prefix1, 'se')
            self.assertEqual(oAddr.name1, 'kelly')
            self.assertEqual(oAddr.sttype1, 'st')
            self.assertEqual(oAddr.city1, 'portland')
            self.assertEqual(oAddr.state_id1, 'or')
            self.assertEqual(oAddr.zip_code1, 97206)
            self.assertEqual(oAddr.prefix2, 'se')
            self.assertEqual(oAddr.name2, '49th')
            self.assertEqual(oAddr.sttype2, 'ave')
            self.assertEqual(oAddr.city2, 'portland')
            self.assertEqual(oAddr.state_id2, 'or')
            self.assertEqual(oAddr.zip_code2, 97206)

        def testPortlandORPointAddress(self):
            sAddr = 'POINT(-123.120000 45.000000)'
            sMode = 'portlandor'
            oAddr = get(sAddr, sMode)
            self.assert_(isinstance(oAddr, address.PointAddress))
            self.assert_(isinstance(oAddr, address.IntersectionAddress))
            self.assertAlmostEqual(oAddr.x, -123.120000)
            self.assertAlmostEqual(oAddr.y, 45.000000)
            
        def testPortlandORNodeAddress(self):
            iAddr = 4
            sAddr = str(iAddr)
            sMode = 'portlandor'
            oAddr = get(sAddr, sMode)
            self.assert_(isinstance(oAddr, address.IntersectionAddress))
            self.assertEqual(oAddr.node_id, iAddr)
            
    unittest.main()
    
