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

This file sets up the model API by exposing the database module & its engine
and all of the model/domain/entity classes.

"""
# TODO: I'd rather just import db and use it directly, which implies removing
#       the DB class and moving its methods to db module functions
#       [wlb 2/23/07]
from byCycle.model import db
_db = db.DB()

# Expose domain/entity classes via model API
from byCycle.model.domain import *
from byCycle.model.address import *


# Expose ``engine`` via the model API
engine = _db.engine
