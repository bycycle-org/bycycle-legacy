###########################################################################
# $Id$
# Created 2006-09-19.
#
# byCycle Services Package.
#
# Copyright (C) 2006 Wyatt Baldwin, byCycle.org <wyatt@bycycle.org>.
# All rights reserved.
#
# For terms of use and warranty details, please see the LICENSE file included
# in the top level of this distribution. This software is provided AS IS with
# NO WARRANTY OF ANY KIND.


"""Provides a base class for the byCycle core services."""
from byCycle.model import db, regions
from byCycle.model.region import Region


class Service(object):
    """Base class for byCycle services."""

    def __init__(self, region=None, dbh=None):
        """Connect to database, iff not alreay connected.

        ``region`` `Region` | `string` | `None` -- Either a region key or a
        `Region` object. In the first case a new `Region` will be instantiated
        to geocode the address; in the second, the object will be used
        directly. ``region`` need not be specified; if it isn't, a specific
        service can try to guess it (most likely via the Address Normalization
        service). ``region`` may also be None; any other type of object will
        raise a ValueError.

        ``dbh`` `DB` -- A database handler. We only want to set this once. It
        may be set directly with a `DB` instance or indirectly by setting
        `region`. Once it has been set, it shouldn't change. However, it can
        be changed by accessing the `_region` attribute. ``dbh`` may also be
        None; any other type of object will raise a ValueError.

        raise `ValueError`
          - ``dbh`` is not a `DB` instance or None.
          - ``region`` is not `Region` instance, a known region key or alias,
            or None.

        """
        self.dbh = dbh
        self.region = region

    def _get_region(self):
        try:
            return self._region
        except AttributeError:
            return None
    def _set_region(self, region):
        """Set `region` to ``region``, iff `region` is not already set.

        Also, initialize `dbh` with `region`.

        ``region`` `Region` | `str` | `None` -- See __init__ for details.

        """
        # See if `region` is already set as a `Region` for this `Service`
        try:
            self._region
        except AttributeError:
            pass
        else:
            if isinstance(self._region, Region):
                # `region` is already set for this `Service`--nothing to do
                return

        # `region` is not set at all or is not a `Region`
        _region = regions.getRegion(region)

        if isinstance(_region, Region):
            self._region = _region
            self.dbh = db.DB(self._region)
    region = property(_get_region, _set_region)

    def _get_db(self):
        return self._dbh
    def _set_db(self, dbh):
        """Set `dbh` to ``dbh`` if ``dbh`` and `dbh` is not already set.

        ``dbh`` `DB` -- See __init__ for details.

        """
        try:
            if isinstance(self._dbh, db.DB):
                return
        except AttributeError:
            self._dbh = None
        if dbh is None:
            return
        if isinstance(dbh, db.DB):
            self._dbh = dbh
            self._region = dbh.region
            self.session = dbh.session
        else:
            raise ValueError('Wrong type for Service dbh: %s' % type(dbh))
    dbh = property(_get_db, _set_db)

    def _beforeQuery(self, q, region=None, dbh=None):
        """Make an attempt to initialize the DB before doing the query."""
        self.dbh = dbh
        self.region = region

    def query(self, q, region=None, dbh=None):
        """Query this service.

         If ``db`` is given, do query via ``db``. If ``region`` is given and
         ``db`` isn't, do query in region. If neither is given, assume the
         specific service is going to guess the region and set `region`/`dbh`
         accordingly.

        This method is used to do initialization that might need to be done
        before any type of query (like making sure there's a database
        connection).

        ``q`` `string` -- The query string.

        ``region`` `Region` | `string` -- See `__init__` for details.

        ``dbh`` `DB` -- See `__init__` for details.

        return `string` -- Just return ``q`` for now

        """
        self._beforeQuery(q, region=region, dbh=dbh)
        return q
