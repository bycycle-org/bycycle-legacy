################################################################################
# $Id$
# Created 2006-??-??.
#
# Address Normalization service.
#
# Copyright (C) 2006-2008 Wyatt Baldwin, byCycle.org <wyatt@bycycle.org>.
# All rights reserved.
#
# For terms of use and warranty details, please see the LICENSE file included
# in the top level of this distribution. This software is provided AS IS with
# NO WARRANTY OF ANY KIND.
################################################################################
import unittest
from bycycle.core.services.normaddr import *
from bycycle.core.model import address, db
from bycycle.core.model.entities import Region, StreetName
from sqlalchemy import *


class TestGetCrossStreets(unittest.TestCase):

    service = Service()

    def _testGood(self, addrs):
        for addr in addrs:
            streets = self.service._getCrossStreets(addr)
            self.assertEqual(len(streets), 2)

    def _testBad(self, addrs):
        for addr in addrs:
            self.assertRaises(ValueError, self.service._getCrossStreets, addr)

    def test_And(self):
        addrs = ('A and B', 'A And B', 'A aNd B', 'A anD B', 'A AND B')
        self._testGood(addrs)

    def test_At(self):
        addrs = ('A at B', 'A At B', 'A aT B', 'A AT B')
        self._testGood(addrs)

    def test_AtSymbol(self):
        addrs = ('A @ B', 'A @B', 'A@ B', 'A@B')
        self._testGood(addrs)

    def test_ForwardSlash(self):
        addrs = ('A / B', 'A /B', 'A/ B', 'A/B')
        self._testGood(addrs)

    def test_BackSlash(self):
        addrs = (r'A \ B', r'A \B', r'A\ B', r'A\B')
        self._testGood(addrs)

    def test_Plus(self):
        addrs = ('A + B', 'A +B', 'A+ B', 'A+B')
        self._testGood(addrs)

    def test_MissingInternalSpace(self):
        addrs = ('A andB', 'Aat B')
        self._testBad(addrs)

    def test_MissingFromOrTo(self):
        addrs = ('and B', 'A at', ' and B', 'A at ')
        self._testBad(addrs)

    def test_MissingFromAndTo(self):
        addrs = ('and', ' and', 'and ', ' and ')
        self._testBad(addrs)


class TestGetNumberAndStreet(unittest.TestCase):

    service = Service()

    def _testGood(self, addrs):
        for addr in addrs:
            num, street_name = self.service._getNumberAndStreetName(addr)
            self.assertEqual(type(num), int)
            self.assertEqual(type(street_name), str)

    def _testBad(self, addrs):
        for addr in addrs:
            self.assertRaises(
                ValueError, self.service._getNumberAndStreetName, addr
            )

    def test_Good(self):
        addrs = ('633 Alberta', '633 N Alberta', '633 N Alberta St',
                 '633 N Alberta St Portland',
                 '633 N Alberta St, Portland',
                 '633 N Alberta St, Portland, OR 97217',)
        self._testGood(addrs)

    def test_Bad(self):
        addrs = ('633', 'Alberta & Kerby', 'x=-123, y=45')
        self._testBad(addrs)


class TestPortlandOR(unittest.TestCase):

    region = Region.get_by_slug('portlandor')

    def _query(self, q, region=None):
        service = Service(region=region)
        oAddr = service.query(q)
        return oAddr

    ### Edge

    def test_PortlandOR_EdgeAddress(self):
        Edge = self.region.module.Edge

        # Get street name ID for n alberta st
        q = db.Session.query(StreetName)
        q = q.filter_by(prefix='n').filter_by(name='alberta')
        street_name = q.filter_by(sttype='st').first()
        self.assert_(street_name is not None)
        street_name_id = street_name.id

        # Get edge matching 633 N Alberta St
        num = 633
        q = db.Session.query(Edge)
        q = q.filter(Edge.addr_f_l<=num).filter(Edge.addr_t_l>=num)
        edge = q.filter_by(street_name_id=street_name_id).first()
        self.assert_(edge is not None)

        q = '%s-%s' % (num, edge.id)
        oAddr = self._query(q, region='portlandor')
        self.assert_(isinstance(oAddr, address.EdgeAddress))
        self.assert_(isinstance(oAddr, address.PostalAddress))
        self.assertEqual(oAddr.number, num)
        self.assertEqual(oAddr.network_id, edge.id)

        self.assertEqual(str(edge.street_name), 'N Alberta St')

    ### Intersection

    def test_PortlandOR_IntersectionAddress_CityStateZip_Both(self):
        q = 'SE Kelly St, Portland, OR 97206 & SE 49th Ave, Portland, OR 97206'
        oAddr = self._query(q)
        self.assert_(isinstance(oAddr, address.IntersectionAddress))
        self.assertEqual(oAddr.prefix1, 'se')
        self.assertEqual(oAddr.name1, 'kelly')
        self.assertEqual(oAddr.sttype1, 'st')
        self.assertEqual(str(oAddr.city1), 'Portland')
        self.assertEqual(str(oAddr.state1), 'OR')
        self.assertEqual(oAddr.zip_code1, 97206)
        self.assertEqual(oAddr.prefix2, 'se')
        self.assertEqual(oAddr.name2, '49th')
        self.assertEqual(oAddr.sttype2, 'ave')
        self.assertEqual(str(oAddr.city2), 'Portland')
        self.assertEqual(str(oAddr.state2), 'OR')
        self.assertEqual(oAddr.zip_code2, 97206)

    def test_PortlandOR_IntersectionAddress_CityStateZip_1(self):
        q = 'SE Kelly St, Portland, OR 97206 & SE 49th Ave'
        oAddr = self._query(q)
        self.assert_(isinstance(oAddr, address.IntersectionAddress))
        self.assertEqual(oAddr.prefix1, 'se')
        self.assertEqual(oAddr.name1, 'kelly')
        self.assertEqual(oAddr.sttype1, 'st')
        self.assertEqual(str(oAddr.city1), 'Portland')
        self.assertEqual(str(oAddr.state1), 'OR')
        self.assertEqual(oAddr.zip_code1, 97206)
        self.assertEqual(oAddr.prefix2, 'se')
        self.assertEqual(oAddr.name2, '49th')
        self.assertEqual(oAddr.sttype2, 'ave')
        self.assertEqual(str(oAddr.city2), 'Portland')
        self.assertEqual(str(oAddr.state2), 'OR')
        self.assertEqual(oAddr.zip_code2, 97206)

    def test_PortlandOR_IntersectionAddress_CityStateZip_2(self):
        q = 'SE Kelly St & SE 49th Ave, Portland, OR 97206'
        oAddr = self._query(q)
        self.assert_(isinstance(oAddr, address.IntersectionAddress))
        self.assertEqual(oAddr.prefix1, 'se')
        self.assertEqual(oAddr.name1, 'kelly')
        self.assertEqual(oAddr.sttype1, 'st')
        self.assertEqual(str(oAddr.city1), 'Portland')
        self.assertEqual(str(oAddr.state1), 'OR')
        self.assertEqual(oAddr.zip_code1, 97206)
        self.assertEqual(oAddr.prefix2, 'se')
        self.assertEqual(oAddr.name2, '49th')
        self.assertEqual(oAddr.sttype2, 'ave')
        self.assertEqual(str(oAddr.city2), 'Portland')
        self.assertEqual(str(oAddr.state2), 'OR')
        self.assertEqual(oAddr.zip_code2, 97206)

    ### Node

    def test_PortlandOR_NodeAddress(self):
        iAddr = 4
        q = str(iAddr)
        oAddr = self._query(q, region='portlandor')
        self.assert_(isinstance(oAddr, address.IntersectionAddress))
        self.assertEqual(oAddr.network_id, iAddr)

    ### Point

    def _test_PortlandOR_PointAddress_Kwargs_Region(self):
        qs = (
            'x=-122.67334, y=45.523307',
            'y=45.523307, x=-122.67334',
            'y= 45.523307     , x =  -122.67334',
            'x:-122.67334, y:45.523307',
            'y:45.523307, x:-122.67334',
            'y: 45.523307     , x :  -122.67334',
            'x=-122.67334 y=45.523307',
            'y=45.523307 x=-122.67334',
            'y= 45.523307    x =  -122.67334',
            'x:-122.67334 y=45.523307',
            'y=45.523307, x:-122.67334',
            'y= 45.523307    x :  -122.67334',
        )
        for q in qs:
            oAddr = self._query(q, region='portlandor')
            self.assert_(isinstance(oAddr, address.PointAddress))
            self.assert_(isinstance(oAddr, address.IntersectionAddress))
            self.assertAlmostEqual(oAddr.x, -122.67334)
            self.assertAlmostEqual(oAddr.y, 45.523307)

    def test_PortlandOR_PointAddress_StringTuple_Region(self):
        q = '(-122.67334, 45.523307)'
        oAddr = self._query(q, region='portlandor')
        self.assert_(isinstance(oAddr, address.PointAddress))
        self.assert_(isinstance(oAddr, address.IntersectionAddress))
        self.assertAlmostEqual(oAddr.x, -122.67334)
        self.assertAlmostEqual(oAddr.y, 45.523307)

    ### Postal

    def test_PortlandOR_PostalAddress_NoRegion_CityStateZip(self):
        q = '4807 SE Kelly St, Portland, OR 97206'
        oAddr = self._query(q)
        self.assert_(isinstance(oAddr, address.PostalAddress))
        self.assertEqual(oAddr.number, 4807)
        self.assertEqual(oAddr.prefix, 'se')
        self.assertEqual(oAddr.name, 'kelly')
        self.assertEqual(oAddr.sttype, 'st')
        self.assertEqual(oAddr.city_name, 'portland')
        self.assertEqual(oAddr.state_code, 'or')
        self.assertEqual(oAddr.zip_code, 97206)

    def test_PortlandOR_PostalAddress_MultiWordCity_Region(self):
        q = '4807 SE Kelly St, Oregon City, OR 97206'
        oAddr = self._query(q, region='portlandor')
        self.assert_(isinstance(oAddr, address.PostalAddress))
        self.assertEqual(oAddr.number, 4807)
        self.assertEqual(oAddr.prefix, 'se')
        self.assertEqual(oAddr.name, 'kelly')
        self.assertEqual(oAddr.sttype, 'st')
        self.assertEqual(oAddr.city_name, 'oregon city')
        self.assertEqual(oAddr.state_code, 'or')
        self.assertEqual(oAddr.zip_code, 97206)

    def test_PortlandOR_PostalAddress_MultiWordName_Region(self):
        q = '4807 SE Martin Luther King Jr Boulevard, oregon city or 97206'
        oAddr = self._query(q, region='portland, OR')
        self.assert_(isinstance(oAddr, address.PostalAddress))
        self.assertEqual(oAddr.number, 4807)
        self.assertEqual(oAddr.prefix, 'se')
        self.assertEqual(oAddr.name, 'martin luther king jr')
        self.assertEqual(oAddr.sttype, 'blvd')
        self.assertEqual(oAddr.city_name, 'oregon city')
        self.assertEqual(oAddr.state_code, 'or')
        self.assertEqual(oAddr.zip_code, 97206)

    def test_PortlandOR_PostalAddress_MultiWordState_Region(self):
        q = '4807 SE Kelly Pants St, Oregon City, South Dakota 97206'
        oAddr = self._query(q, region='portlandor')
        self.assert_(isinstance(oAddr, address.PostalAddress))
        self.assertEqual(oAddr.number, 4807)
        self.assertEqual(oAddr.prefix, 'se')
        self.assertEqual(oAddr.name, 'kelly pants')
        self.assertEqual(oAddr.sttype, 'st')
        self.assertEqual(oAddr.city_name, 'oregon city')
        self.assertEqual(oAddr.state_code, 'sd')
        self.assertEqual(oAddr.zip_code, 97206)

    def test_PortlandOR_PostalAddress_NameEndsWithStreetType_Region(self):
        q = '4807 SE Johnson Creek, Oregon City, Oregon 97206'
        oAddr = self._query(q, region='portlandor')
        self.assert_(isinstance(oAddr, address.PostalAddress))
        self.assertEqual(oAddr.number, 4807)
        self.assertEqual(oAddr.prefix, 'se')
        self.assertEqual(oAddr.name, 'johnson creek')
        self.assertEqual(oAddr.sttype, None)
        self.assertEqual(oAddr.city_name, 'oregon city')
        self.assertEqual(oAddr.state_code, 'or')
        self.assertEqual(oAddr.zip_code, 97206)


if __name__ == '__main__':
    unittest.main()