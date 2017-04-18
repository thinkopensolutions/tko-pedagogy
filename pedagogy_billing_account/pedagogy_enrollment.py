# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Thinkopen Solutions, Lda. All Rights Reserved
#    http://www.thinkopensolutions.com.
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv


class pedagogy_enrollment(osv.osv):
    _inherit = 'pedagogy.enrollment'

    def _get_payments(self, cr, uid, enroll):
        pool = self.pool.get('pedagogy.billing.line')
        query = [('bill_id.enrollment_id', '=', enroll.id),
                 ('bill_id.state', 'in', ['confirm', 'invoiced', 'paid']),
                 ('billing_category_id.code', '=', 'BASE')]
        return pool.browse(cr, uid, pool.search(cr, uid, query))
