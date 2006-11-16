################################################################################
# $Id$
# Created 2005-11-07.
#
# Database Abstraction Layer.
#
# Copyright (C) 2006 Wyatt Baldwin, byCycle.org <wyatt@bycycle.org>.
# All rights reserved.
#
# For terms of use and warranty details, please see the LICENSE file included
# in the top level of this distribution. This software is provided AS IS with
# NO WARRANTY OF ANY KIND.
################################################################################
"""Database initialization and handling.

TODO:
  - Use fancy-pants ORM (SQLAlchemy, for example) to create proper model/domain
    objects.
  - Decouple regions from this class (i.e., they shouldn't be subclasses)--when
    moving to using an ORM, move the region-common stuff into a Region base
    class.
  - Make createAdjacencyMatrix available through bycycle script.
  - Should DB class be a Singleton (per region)???

"""
import os
import math

import psycopg2
import psycopg2.extensions

from sqlalchemy.engine import create_engine
from sqlalchemy.schema import BoundMetaData
from sqlalchemy.orm import create_session


class _DB(object):
    """A database handler for a specific region."""

    def __init__(self, region):
        """Create a database handler for ``region``.

        ``region`` `Region`

        """
        self.region = region
        self.schema = region.key
        self.engine = create_engine('postgres://', creator=self.createConnection)
        self.metadata = BoundMetaData(self.engine)
        self.raw_metadata = BoundMetaData(self.engine)
        self.session = create_session(bind_to=self.engine)

    def createConnection(self):
        """Set up and return underlying DB connection."""
        pw_path = os.path.join(self.region.model_path, '.pw')
        pw_file = file(pw_path)
        pw = pw_file.read().strip()
        pw_file.close()
        return psycopg2.connect(
            database='bycycle',
            user='bycycle',
            password=pw
        )

    def getById(self, mapper, table, *ids):
        """Get objects from ``table`` using ``mapper`` and order by ``ids``.

        ``ids`` One or more row IDs
        ``mapper`` DB to object mapper
        ``table`` Table to fetch from

        """
        query = self.session.query(mapper)
        objects = query.select(table.c.id.in_(*ids))
        objects_by_id = dict(zip([object.id for object in objects], objects))
        ordered_objects = []
        for i in ids:
            try:
                ordered_objects.append(objects_by_id[i])
            except KeyError:
                # TODO: Should we insert None instead???
                pass
        return ordered_objects

    def turnSQLEchoOff(self):
        """Turn off echoing of SQL statements."""
        self.engine.echo = False

    def turnSQLEchoOn(self):
        """Turn on echoing of SQL statements."""
        self.engine.echo = True

    def vacuum(self, *tables):
        """Vacuum ``tables`` or all tables if ``tables`` not given."""
        self.connection.set_isolation_level(0)
        if not tables:
            self.cursor.execute('VACUUM FULL ANALYZE')
        else:
            for table in tables:
                self.cursor.execute('VACUUM FULL ANALYZE %s' % table)
        self.connection.set_isolation_level(2)

    def __del__(self):
        try:
            self.session.close()
        except:
            pass


__db = None

def DB(*args, **kwargs):
    global __db
    if __db is None:
        __db = _DB(*args, **kwargs)
    return __db