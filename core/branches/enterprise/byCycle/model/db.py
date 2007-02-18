################################################################################
# $Id$
# Created 2005-11-07.
#
# Database Connection Handler.
#
# Copyright (C) 2006 Wyatt Baldwin, byCycle.org <wyatt@bycycle.org>.
# All rights reserved.
#
# For terms of use and warranty details, please see the LICENSE file included
# in the top level of this distribution. This software is provided AS IS with
# NO WARRANTY OF ANY KIND.
################################################################################
"""Database connection initialization and handling.

Provides the ``DB`` class, which connects to the database and contains various
generic (i.e., not region-specific) database functions.

TODO: The ``DB`` class is a (poorly implemented) Singleton. Ian Bicking thinks
Singletons are stupid. At the very least, we should use a better
implementation.

"""
import os
import math

import psycopg2
import psycopg2.extensions

from sqlalchemy.engine import create_engine
from sqlalchemy.schema import BoundMetaData
from sqlalchemy.orm import create_session


class _DB(object):
    """Global database connection handler."""

    def __init__(self):
        """Create the global (Singleton) database handler."""
        self.model_path = os.path.abspath(os.path.dirname(__file__))        
        self.engine = create_engine('postgres://', creator=self.createConnection)
        self.metadata = BoundMetaData(self.engine)
        self.raw_metadata = BoundMetaData(self.engine)
        self.session = create_session(bind_to=self.engine)

    def createConnection(self):
        """Set up and return underlying DB connection."""
        pw_path = os.path.join(self.model_path, '.pw')
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
        
        return `list`
          A list of domain objects corresponding to the IDs passed via ``ids``.
          Any ID in ``ids`` that doesn't correspond to a row in ``table`` will
          be ignored (for now), so the list may not contain the same number of
          objects as len(ids). If ``ids`` is empty, an empty list is returned.

        """
        query = self.session.query(mapper)
        objects = query.select(table.c.id.in_(*ids))
        objects_by_id = dict(zip([object.id for object in objects], objects))
        ordered_objects = []
        for i in ids:
            try:
                ordered_objects.append(objects_by_id[i])
            except KeyError:
                # No row with ID==i in ``table``
                # TODO: Should we insert None instead or raise???
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
