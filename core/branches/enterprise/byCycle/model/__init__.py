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
from byCycle.model import db

# Expose domain/entity classes via model API
from byCycle.model.domain import *
from byCycle.model.address import *


# Expose ``engine`` via the model API
engine = db.engine
