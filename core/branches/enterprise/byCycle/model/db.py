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

"""
from __future__ import with_statement

import os

from sqlalchemy.engine import create_engine
from sqlalchemy.orm import create_session

import elixir

from byCycle import install_path


model_path = os.path.join(install_path, 'model')
metadata = elixir.metadata

def __init__():
    global engine
    engine = create_engine(getConnectionUri())

def getConnectionUri():
    """Get database connection URI (DSN)."""
    dburi = 'postgres://bycycle:%s@localhost/bycycle'
    pw_path = os.path.join(model_path, '.pw')
    with file(pw_path) as pw_file:
        password = pw_file.read().strip()
    return dburi % (password)

def connectMetadata(metadata=elixir.metadata):
    """Connect ``metadata`` to ``engine``."""
    metadata.connect(engine)

def makeSession():
    connectMetadata()
    return create_session(bind_to=engine)

def createAll():
    turnSQLEchoOn()
    metadata.create_all()
    turnSQLEchoOff()

def dropAll():
    turnSQLEchoOn()
    metadata.drop_all()
    turnSQLEchoOff()

def getById(class_or_mapper, session, *ids):
    """Get objects and order by ``ids``.

    ``class_or_mapper`` Entity class or DB to object mapper
    ``session`` DB session
    ``ids`` One or more row IDs

    return `list`
      A list of domain objects corresponding to the IDs passed via ``ids``.
      Any ID in ``ids`` that doesn't correspond to a row in ``table`` will
      be ignored (for now), so the list may not contain the same number of
      objects as len(ids). If ``ids`` is empty, an empty list is returned.

    """
    query = session.query(class_or_mapper)
    objects = query.select(class_or_mapper.c.id.in_(*ids))
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

def turnSQLEchoOff():
    """Turn off echoing of SQL statements."""
    engine.echo = False

def turnSQLEchoOn():
    """Turn on echoing of SQL statements."""
    engine.echo = True

def vacuum(*tables):
    """Vacuum ``tables`` or all tables if ``tables`` not given."""
    connection.set_isolation_level(0)
    if not tables:
        cursor.execute('VACUUM FULL ANALYZE')
    else:
        for table in tables:
            cursor.execute('VACUUM FULL ANALYZE %s' % table)
    connection.set_isolation_level(2)


__init__()
