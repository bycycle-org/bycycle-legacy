if __name__ == '__main__':
    import unittest
    from byCycle.tripplanner.services.geocode import *
    from byCycle.tripplanner.model import portlandor

    class DontTestMilwaukee(unittest.TestCase):
        A = {#' ',
            # Milwaukee
            'milwaukeewi':
            ('0 w hayes ave',
             'lon=-87.940407, lat=43.05321',
             'lon=-87.931137, lat=43.101234',
             'lon=-87.934399, lat=43.047126',
             '125 n milwaukee',
             '125 n milwaukee milwaukee wi',
             '27th and lisbon',
             '27th and lisbon milwaukee',
             '27th and lisbon milwaukee, wi',
             'lon=-87.961178, lat=43.062993',
             'lon=-87.921953, lat=43.040791',
             'n 8th st & w juneau ave, milwaukee, wi ',
             '77th and burleigh',
             '2750 lisbon',
             '(-87.976885, 43.059544)',
             'lon=-87.946243, lat=43.041669',
             '124th and county line',
             '124th and county line wi',
             '5th and center',
             '6th and hadley',
             )}

    class TestPortlandOR(unittest.TestCase):
        def _get(self, q):
            region = 'portlandor'
            return get(region, q)
        
        def testPostalAddress(self):
            q = '633 n alberta'
            geocodes = self._get(q)
            self.assert_(len(geocodes) == 1)
            q = '37800 S Hwy 213 Hwy, Clackamas, OR 97362'
            geocodes = self._get(q)
            self.assert_(len(geocodes) == 1)
            
        def testPostalAddressMultipleMatches(self):
            q = '633 alberta'
            self.assertRaises(MultipleMatchingAddressesError, self._get, q)
            try:
                self._get(q)
            except MultipleMatchingAddressesError, e:
                self.assert_(len(e.geocodes) == 2)
                
            q = '300 main'
            self.assertRaises(MultipleMatchingAddressesError, self._get, q)
            try:
                self._get(q)
            except MultipleMatchingAddressesError, e:
                self.assert_(len(e.geocodes) == 12)

        def testPostalAddressNoSuffixOnNumberStreetName(self):
            q = '4550 ne 15'
            geocodes = self._get(q)
            self.assert_(len(geocodes) == 1)            

        def testPostalAddressWithSuffixOnNumberStreetName(self):
            q = '4550 ne 15th'
            geocodes = self._get(q)
            self.assert_(len(geocodes) == 1)            

        def testPostalAddressNoState(self):
            q = '4408 se stark'
            geocodes = self._get(q)
            self.assert_(len(geocodes) == 1)
            
        def testPostalAddressNoState(self):
            q = '4408 se stark, or'
            geocodes = self._get(q)
            self.assert_(len(geocodes) == 1)

        def testPostalAddressAllPartsNoCommas(self):
            q = '4408 se stark st oregon 97215'
            geocodes = self._get(q)
            self.assert_(len(geocodes) == 1)
            
        def testPostalAddressBadState(self):
            q = '4408 se stark, wi'
            self.assertRaises(AddressNotFoundError, self._get, q)

        def testPostalAddressBadState(self):
            q = '300 bloofy lane'
            self.assertRaises(AddressNotFoundError, self._get, q)
            
        def testIntersectionAddress(self):
            q = '44th and stark'
            geocodes = self._get(q)
            self.assert_(len(geocodes) == 1)
            q = 'W Burnside St, Portland, OR 97204 & ' \
                'NW 3rd Ave, Portland, OR 97209'
            geocodes = self._get(q)
            self.assert_(len(geocodes) == 1)
            q = 'Burnside St, Portland, & 3rd Ave, Portland, OR 97209'
            geocodes = self._get(q)
            self.assert_(len(geocodes) == 1)
            
        def testIntersectionAddressMultipleMatches(self):
            q = '3rd @ main'
            self.assertRaises(MultipleMatchingAddressesError, self._get, q)
            try:
                self._get(q)
            except MultipleMatchingAddressesError, e:
                self.assert_(len(e.geocodes) == 10)

        def testIntersectionAddressDisambiguatedMultipleMatch(self):
            q = '3rd @ main 97024'
            geocodes = self._get(q)
            self.assert_(len(geocodes) == 1)
            
        def testPointAddressWKT(self):
            q = 'point(-120.432129 46.137977)'
            geocodes = self._get(q)
            self.assert_(len(geocodes) == 1)
            q = 'point(-120.025635 45.379161)'
            geocodes = self._get(q)
            self.assert_(len(geocodes) == 1)
        
        def testPointAddressStringTuple(self):
            q = '(-122.67334, 45.523307)'
            geocodes = self._get(q)
            self.assert_(len(geocodes) == 1)
            q = '-122.67334, 45.523307'
            geocodes = self._get(q)
            self.assert_(len(geocodes) == 1)
            
        def testPointAddressKwargsString(self):
            q = 'x=-120.432129, y=46.137977'
            geocodes = self._get(q)
            self.assert_(len(geocodes) == 1)

        def testPointAddressPositionalKwargsString(self):
            q = 'asldfj=-123.432129, aass=46.137977'
            geocodes = self._get(q)
            self.assert_(len(geocodes) == 1)

    unittest.main()
