################################################################################
# $Id$
# Created ???.
#
# Geocode service.
#
# Copyright (C) 2006 Wyatt Baldwin, byCycle.org <wyatt@bycycle.org>.
# All rights reserved.
#
# For terms of use and warranty details, please see the LICENSE file included
# in the top level of this distribution. This software is provided AS IS with
# NO WARRANTY OF ANY KIND.
################################################################################
"""
Provides geocoding via the `query` method of the `Service` class.

Geocoding is the process of determining a location on earth associated with a
an address (or other feature). This service also determines which network
features input addresses are associated with and supplies this information
through the `Geocode` class as a node or edge ID, depending on the type of the
input address.

The service recognizes these types of addresses, which are first normalized by
the Address Normalization service (normaddr):

- Postal (e.g., 633 N Alberta, Portland, OR)
- Intersection (e.g., Alberta & Kerby)
- Point (e.g., x=-123, y=45)
- Node (i.e., node ID)
- Edge (i.e., number + edge ID).

"""
from sqlalchemy import orm
from sqlalchemy.sql import select, func, and_, or_
from sqlalchemy.exceptions import InvalidRequestError

from byCycle.model import db
from byCycle.model.address import *
from byCycle.model.geocode import *
from byCycle.model.domain import StreetName, City, State, Place
from byCycle.model.domain import Edge, Node, Point

from byCycle import services
from byCycle.services import normaddr
from byCycle.services import identify
from byCycle.services.exceptions import *


class GeocodeError(ByCycleError):
    """Base Error class for Geocode service."""
    def __init__(self, desc='Geocode Error'):
        ByCycleError.__init__(self, desc)

class AddressNotFoundError(GeocodeError, NotFoundError):
    def __init__(self, desc='Address Not Found', address='', region=''):
        if region and address:
            desc = ('Unable to find address "%s" in region "%s"' %
                    (address, region.title))
        GeocodeError.__init__(self, desc=desc)

class MultipleMatchingAddressesError(GeocodeError):
    def __init__(self, desc='Multiple Matches Found', geocodes=[]):
        self.geocodes = geocodes
        GeocodeError.__init__(self, desc=desc)


class Service(services.Service):
    """Geocoding Service."""

    name = 'geocode'

    def __init__(self, region=None):
        services.Service.__init__(self, region=region)

    def query(self, q):
        """Find and return `Geocodes` in ``region`` matching the address ``q``.

        Choose the appropriate geocoding method based on the type of the input
        address. Call the geocoding method and return a `Geocode`. If the
        input address can't be found or there is more than one match for it,
        an exception will be raised.

        ``q`` `string`
            An address to be normalized & geocoded in the given ``region``.

        return `Geocode`
            A `Geocode` object corresponding to the input address, ``q``.

        raise `ValueError`
            Type of input address can't be determined

        raise `InputError`, `ValueError`
            Some are raised in the normaddr query. Look there for details.

        raise `AddressNotFoundError`
            The address can't be geocoded

        raise `MultipleMatchingAddressesError`
            Multiple address found that match the input address, ``q``

        """
        # First, normalize the address, getting back an `Address` object.
        # The NA service may find a region, iff `region` isn't already set. If
        # so, we want to use that region as the region for this query.
        na_service = normaddr.Service(region=self.region)
        oAddr = na_service.query(q)
        self.region = na_service.region
        if isinstance(oAddr, (NodeAddress, PointAddress)):
            geocodes = self.getPointGeocodes(oAddr)
        elif isinstance(oAddr, (EdgeAddress, PostalAddress)):
            geocodes = self.getPostalGeocodes(oAddr)
        elif isinstance(oAddr, IntersectionAddress):
            try:
                geocodes = self.getIntersectionGeocodes(oAddr)
            except AddressNotFoundError, _not_found_exc:
                # Couldn't find something like "48th & Main" or "Main & 48th"
                # Try "4800 Main" instead
                try:
                    num = int(oAddr.street_name1.name[:-2])
                except (TypeError, ValueError):
                    try:
                        num = int(oAddr.street_name2.name[:-2])
                    except (TypeError, ValueError):
                        pass
                    else:
                        street_name = oAddr.street_name1
                else:
                    street_name = oAddr.street_name2

                try:
                    postal_addr = PostalAddress(number=num*100,
                                                street_name=street_name,
                                                place=oAddr.place)
                    geocodes = self.getPostalGeocodes(postal_addr)
                except (NameError, UnboundLocalError, AddressNotFoundError), e:
                    # Neither of the cross streets had a number street name OR
                    # the faked postal address couldn't be found.
                    raise _not_found_exc
        else:
            raise ValueError('Could not determine address type for address '
                             '"%s" in region "%s"' %
                             (q, region or '[No region specified]'))

        if len(geocodes) > 1:
            raise MultipleMatchingAddressesError(geocodes=geocodes)

        return geocodes[0]

    ### Each get*Geocode function returns a list of possible geocodes for the
    ### input address or raises an error when no matches are found.

    def getPostalGeocodes(self, oAddr):
        """Geocode postal address represented by ``oAddr``.

        ``oAddr``
            A `PostalAddress` (e.g., 123 Main St, Portland) OR an
            `EdgeAddress`. An edge "address" contains just street number and
            ID of some edge.

        return `list`
            A list of `PostalGeocode`s.

        raise ``AddressNotFoundError``
            Address doesn't match any edge in the database.

        """
        geocodes = []
        num = oAddr.number
        table = Edge.table
        c = Edge.c

        clause = [
            (func.least(c.addr_f, c.addr_t) <= num),
            (num <= func.greatest(c.addr_f, c.addr_t))
        ]

        try:
            # Try to look up edge by network ID first
            network_id = oAddr.network_id
        except AttributeError:
            # No network ID, so look up address by street name and place
            self.append_street_name_where_clause(clause, oAddr.street_name)
            self.append_place_where_clause(clause, oAddr.place)
            edges = Edge.select(and_(*clause))
        else:
            clause.append(c.id == network_id)
            edges = Edge.select(and_(*clause))

        if not edges:
            raise AddressNotFoundError(address=oAddr, region=self.region)

        # Make list of geocodes for edges matching oAddr
        for e in edges:
            place = e.getPlaceOnSideNumberIsOn(num)
            e_addr = PostalAddress(num, e.street_name, place)
            geocodes.append(PostalGeocode(self.region, e_addr, e))
        return geocodes

    def getIntersectionGeocodes(self, oAddr):
        """Geocode the intersection address represented by ``oAddr``.

        ``oAddr`` -- An `IntersectionAddress` (e.g., 1st & Main, Portland)

        return `list` -- A list of `IntersectionGeocode`s.

        raise `AddressNotFoundError` -- Address doesn't match any edges in the
        database.

        """
        layer_edges = Edge.table

        def get_node_ids(street_name, place):
            node_ids = {}
            c = Edge.c
            select_ = select([c.node_f_id, c.node_t_id])
            self.append_street_name_where_clause(select_, street_name)
            self.append_place_where_clause(select_, place)
            result = select_.execute()
            for row in result:
                node_ids[row.node_f_id] = 1
                node_ids[row.node_t_id] = 1
            result.close()
            return node_ids

        ids_A = get_node_ids(oAddr.street_name1, oAddr.place1)
        if ids_A:
            ids_B = get_node_ids(oAddr.street_name2, oAddr.place2)
        else:
            ids_B = []

        node_ids = [id_ for id_ in ids_A if (id_ in ids_B)]
        if not node_ids:
            raise AddressNotFoundError(address=oAddr, region=self.region)

        # Get node rows matching common node IDs and map to `Node` objects
        nodes = Node.select(Node.c.id.in_(*node_ids))

        if not nodes:
            raise AddressNotFoundError(address=oAddr, region=self.region)

        # Create and return `IntersectionGeocode`s
        geocodes = []
        for node in nodes:
            # TODO: Pick edges that correspond to the input address's cross
            # streets instead of the first two (which is basically choosing at
            # random).
            edges = node.edges
            edge1, edge2 = edges[0], edges[1]
            addr = IntersectionAddress(
                street_name1=edge1.street_name, place1=edge1.place_l,
                street_name2=edge2.street_name, place2=edge2.place_l
            )
            g = IntersectionGeocode(self.region, addr, node)
            geocodes.append(g)
        return geocodes

    def getPointGeocodes(self, oAddr):
        """Geocode point or node address represented by ``oAddr``.

        ``oAddr``
            A `PointAddress` (e.g., POINT(x y)) OR a `NodeAddress`. A node
            "address" contains just the ID of some node.

        return `list`
            A list containing one `IntersectionGeocode` or one
            `PostalGeocode`, depending on whether the point is at an
            intersection with cross streets or a dead end.

        raise `AddressNotFoundError`
            Point doesn't match any nodes in the database.

        """
        try:
            # Special case of `Node` ID supplied directly
            node_id = oAddr.network_id
        except AttributeError:
            # No network ID, so look up `Node` by distance
            id_service = identify.Service(region=self.region)
            try:
                node = id_service.query(oAddr.point, layer='node')
            except IdentifyError:
                pass
        else:
            try:
                node = Node.selectone(Node.c.id == node_id)
                node = getattr(node, '%s_node' % self.region.slug)
            except InvalidRequestError:
                pass

        # TODO: Check the `Edge`'s street names and places for [No Name]s and
        # choose the `Edge`(s) that have the least of them. Also, we should
        # pick streets that have different names from each other when creating
        # `IntersectionAddresses`s
        try:
            edges = node.base.edges
        except UnboundLocalError:
            raise AddressNotFoundError(region=self.region, address=oAddr)
        if len(edges) > 1:
            # `node` has multiple outgoing edges
            edge1, edge2 = edges[0], edges[1]
            addr = IntersectionAddress(
                street_name1=edge1.street_name, place1=edge1.place_l,
                street_name2=edge2.street_name, place2=edge2.place_l
            )
            g = IntersectionGeocode(self.region, addr, node)
        else:
            # `node` is at a dead end
            edge = edges[0]
            # Set address number to number at `node` end of edge
            if node.id == edge.node_f_id:
                num = edge.addr_f
            else:
                num = edge.addr_t
            addr = PostalAddress(num, edge.street_name, edge.place_l)
            g = PostalGeocode(self.region, addr, edge)
            g.node = node
        return [g]

    ### Utilities

    def get_street_name_ids(self, street_name):
        """Get a WHERE clause for ``street_name``."""
        clause = []
        for name in ('prefix', 'name', 'sttype', 'suffix'):
            val = getattr(street_name, name)
            if val:
                clause.append(StreetName.c[name] == val)
        if clause:
            result = select([StreetName.c.id], and_(*clause)).execute()
            return [r.id for r in result]
        return []

    def append_street_name_where_clause(self, append_to, street_name):
        if street_name:
            st_name_ids = self.get_street_name_ids(street_name)
            clause = Edge.c.street_name_id.in_(*st_name_ids)
            if isinstance(append_to, (list, tuple)):
                append_to.append(clause)
            else:
                append_to.append_whereclause(clause)

    def get_place_ids(self, place):
        """Get ``Place`` ``place``."""
        clause = []
        if place.city_name:
            r = select([City.c.id], (City.c.city == place.city_name)).execute()
            city_id = r.fetchone().id if r else None
            clause.append(Place.c.city_id == city_id)
        if place.state_code:
            r = select([State.c.id], (State.c.code == place.state_code)).execute()
            state_id = r.fetchone().id if r else None
            clause.append(Place.c.state_id == state_id)
        if place.zip_code:
            clause.append(Place.c.zip_code == place.zip_code)
        if clause:
            result = select([Place.c.id], and_(*clause)).execute()
            return [r.id for r in result]
        return []

    def append_place_where_clause(self, append_to, place):
        if place:
            place_ids = self.get_place_ids(place)
            c = Edge.c
            clause = or_(
                c.place_l_id.in_(*place_ids),
                c.place_r_id.in_(*place_ids)
            )
            if isinstance(append_to, (list, tuple)):
                append_to.append(clause)
            else:
                append_to.append_whereclause(clause)
