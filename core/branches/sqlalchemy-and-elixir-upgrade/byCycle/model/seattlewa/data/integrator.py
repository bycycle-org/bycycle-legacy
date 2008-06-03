###############################################################################
# $Id: shp2pgsql.py 187 2006-08-16 01:26:11Z bycycle $
# Created 2007-05-31
#
# Seattle, WA, data integrator.
#
# Copyright (C) 2007 Wyatt Baldwin, byCycle.org <wyatt@bycycle.org>.
# All rights reserved.
#
# For terms of use and warranty details, please see the LICENSE file included
# in the top level of this distribution. This software is provided AS IS with
# NO WARRANTY OF ANY KIND.
###############################################################################
from byCycle.model.data import integrator
from byCycle.model import db


class Integrator(integrator.Integrator):

    def __init__(self, *args, **kwargs):
        super(Integrator, self).__init__(*args, **kwargs)

    def shp2db(self):
        """Convert shapefile to raw SQL. Add dummy columns."""
        super(Integrator, self).shp2db()
        raw_table = 'raw.seattlewa'
        db.addColumn(raw_table, 'city_r', 'int4')
        db.execute('update %s set city_r = 0' % raw_table)
        db.addColumn(raw_table, 'one_way', 'int4')
        db.execute('update %s set one_way = 3' % raw_table)
        db.commit()

    def get_state_code_for_city(self, city):
        return 'wa'
