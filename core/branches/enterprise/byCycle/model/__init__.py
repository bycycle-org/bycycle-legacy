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

# TODO: I'd rather just import db and use it directly, which implies removing
#       the DB class and moving its methods to db module functions
#       [wlb 2/23/07]
from byCycle.model import db
_db = db.DB()

from byCycle.model.domain import *


def connect():
    """Connect the elixir dynamic metadata to database handler's engine.

    Connects in the context of the current thread.

    Note: this doesn't connect to the database; it just wires elixir's
    dynamic metadata object up to the engine.

    """
    elixir.metadata.connect(_db.engine)

def create_all():
    """Create all Entity tables that don't already exist."""
    _db.turnSQLEchoOn()
    connect()
    elixir.create_all()
    _db.turnSQLEchoOff()
