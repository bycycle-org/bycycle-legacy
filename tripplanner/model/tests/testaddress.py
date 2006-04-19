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
            self.assertEqual(str(a), '4807 SE Kelly St, Portland, OR 97206')
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
            sAddr = 'SE Kelly St & SE 49th Ave, Portland, OR 97206'
            assert(str(a) == sAddr)


    class testPointAddress(unittest.TestCase):
        def testPointAddress(self):
            a = PointAddress(x=-123.12, y=45)
            print a
            self.assertEqual(str(a), 'POINT(-123.120000 45.000000)')


    unittest.main()
