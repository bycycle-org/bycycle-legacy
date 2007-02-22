################################################################################
# $Id$
# Created ???.
#
# byCycle model package
#
# Copyright (C) 2006 Wyatt Baldwin, byCycle.org <wyatt@bycycle.org>.
# All rights reserved.
#
# For terms of use and warranty details, please see the LICENSE file included
# in the top level of this distribution. This software is provided AS IS with
# NO WARRANTY OF ANY KIND.
################################################################################
"""
byCycle model package.

"""
import elixir
from elixir import Entity, Unicode
from elixir import has_field, using_options

from byCycle.model import db


# Get the global database handler
_db = db.DB()

def connect():
    """Connect the elixir dynamic metadata to database handler's engine.

    Connects in the context of the current thread.

    Note: this doesn't connect to the database; it just wires elixir's
    dynamic metadata object up to the engine.
    
    """
    elixir.metadata.connect(_db.engine)

def create_all():
    _db.turnSQLEchoOn()
    connect()
    elixir.create_all()
    _db.turnSQLEchoOff()


class Region(Entity):
    has_field('title', Unicode)
    using_options(tablename='regions')
    
