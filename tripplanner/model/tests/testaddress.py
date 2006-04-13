if __name__ == "__main__":
    import unittest
    from byCycle.tripplanner.model.address import *

    class TestPostalAddress(unittest.TestCase):
        def testPostalAddress(self):
            a = PostalAddress(number='4807',
                              prefix='SE',
                              name='Kelly',
                              sttype='St',
                              city='Portland',
                              state='OR',
                              zip_code=97206)
            assert(str(a) == '4807 SE Kelly St\nPortland, OR 97206')


    class TestIntersectionAddress(unittest.TestCase):
        def testIntersectionAddress(self):
            a = IntersectionAddress(prefix1='SE',
                                    name1='Kelly',
                                    sttype1='St',
                                    city1='Portland',
                                    state1='OR',
                                    zip_code1=97206,
                                    prefix2='SE',
                                    name2='49th',
                                    sttype2='Ave',
                                    city2='Portland',
                                    state2='OR',
                                    zip_code2=97206)
            assert(str(a) == 'SE Kelly St & SE 49th Ave\n'
                   'Portland, OR 97206')


    class testPointAddress(unittest.TestCase):
        def testPointAddress(self):
            a = PointAddress(x=-123.12, y=45)
            assert(str(a) == 'POINT(-123.120000 45.000000)')


    unittest.main()
