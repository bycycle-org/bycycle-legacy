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
if __name__ == "__main__":
    import unittest
    from byCycle.tripplanner.model.address import *

    class TestPostalAddress(unittest.TestCase):
        def testPostalAddress(self):
            a = PostalAddress(number='4807',
                              street=Street(prefix='SE',
                                            name='Kelly',
                                            sttype='St'),
                              place=Place(city='Portland',
                                          state_id='OR',
                                          zip_code=97206))
            self.assertEqual(str(a), '4807 SE Kelly St\nPortland, OR 97206')
            a.prefix = 'N';
            self.assertEqual(a.prefix, 'N')
            self.assertEqual(a.street.prefix, 'N')
            a.name = 'Alberta'
            self.assertEqual(a.name, 'Alberta')
            self.assertEqual(a.street.name, 'Alberta')
            a.sttype = 'Rd'
            self.assertEqual(a.sttype, 'Rd')
            self.assertEqual(a.street.sttype, 'Rd')
            a.suffix = 'SB'
            self.assertEqual(a.suffix, 'SB')
            self.assertEqual(a.street.suffix, 'SB')


    class TestIntersectionAddress(unittest.TestCase):
        def testIntersectionAddress(self):
            a = IntersectionAddress(street1=Street(prefix='SE',
                                                   name='Kelly',
                                                   sttype='St'),
                                    place1=Place(city='Portland',
                                                 state_id='OR',
                                                 zip_code=97206),
                                    street2=Street(prefix='SE',
                                                   name='49th',
                                                   sttype='Ave'),
                                    place2=Place(city='Portland',
                                                 state_id='OR',
                                                 zip_code=97206))
            sAddr = 'SE Kelly St & SE 49th Ave\nPortland, OR 97206'
            assert(str(a) == sAddr)


    class testPointAddress(unittest.TestCase):
        def testPointAddress(self):
            a = PointAddress(x=-123.12, y=45)
            self.assertEqual(str(a), 'POINT(-123.120000 45.000000)')


    unittest.main()
