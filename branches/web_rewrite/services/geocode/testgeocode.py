"""$Id$

Description goes here.

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
if __name__ == '__main__':
    import unittest
    from byCycle.services.geocode import *
    from byCycle.model import portlandor

    class DontTestMilwaukee(unittest.TestCase):
        A = {#' ',
            # Milwaukee
            'milwaukeewi':
            ('0 w hayes ave',
             'x=-87.940407, y=43.05321',
             'x=-87.931137, y=43.101234',
             'x=-87.934399, y=43.047126',
             '125 n milwaukee',
             '125 n milwaukee milwaukee wi',
             '27th and lisbon',
             '27th and lisbon milwaukee',
             '27th and lisbon milwaukee, wi',
             'x=-87.961178, y=43.062993',
             'x=-87.921953, y=43.040791',
             'n 8th st & w juneau ave, milwaukee, wi ',
             '77th and burleigh',
             '2750 lisbon',
             '(-87.976885, 43.059544)',
             'x=-87.946243, y=43.041669',
             '124th and county line',
             '124th and county line wi',
             '5th and center',
             '6th and hadley',
             )}

    class TestPortlandOR(unittest.TestCase):
        def _get(self, q):
            region = 'portlandor'
            return get(q=q, region=region)
        
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

        def testEdgeAddress(self):
            q = '633 1651'
            geocodes = self._get(q)
            self.assert_(len(geocodes) == 1)
            
        def testEdgeAddressBadID(self):
            q = '633 16510'
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

        def testIntersectionAddressMidblock(self):
            q = '48th & kelly'
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

        def testNodeAddress(self):
            q = '1651'
            geocodes = self._get(q)
            self.assert_(len(geocodes) == 1)
            
        def testNodeAddressBadID(self):
            q = '84700'
            self.assertRaises(AddressNotFoundError, self._get, q)
            
    unittest.main()
