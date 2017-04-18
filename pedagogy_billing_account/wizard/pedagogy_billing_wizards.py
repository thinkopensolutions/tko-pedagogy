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

DATE_FORMAT = '%Y-%m-%d'


class pedagogy_billing_classes(osv.osv_memory):
    _name = 'pedagogy.billing.class'
    _inherit = 'pedagogy.billing.class'

    def _get_payments_for_period(self, cr, uid, enroll, from_date, to_date):
        convert = lambda dt: dt.strftime(DATE_FORMAT)
        bill_pool = self.pool.get('pedagogy.billing')
        query = [('student_id', '=', enroll.student_id.id),
                 ('state', 'in', ['confirm', 'invoiced', 'paid']),
                 ('enrollment_id', '=', enroll.id),
                 ('line_ids.billing_category_id.code', '=', 'BASE'),
                 ('date_from', '>=', convert(from_date)),
                 ('date_to', '<=', to_date)]
        return len(bill_pool.search(cr, uid, query)) > 0


class pedagogy_billing_students(osv.osv_memory):
    _name = 'pedagogy.billing.students'
    _inherit = 'pedagogy.billing.students'

    def _get_payments_for_period(self, cr, uid, enroll, from_date, to_date):
        convert = lambda dt: dt.strftime(DATE_FORMAT)
        bill_pool = self.pool.get('pedagogy.billing')
        query = [('student_id', '=', enroll.student_id.id),
                 ('state', 'in', ['confirm', 'invoiced', 'paid']),
                 ('enrollment_id', '=', enroll.id),
                 ('line_ids.billing_category_id.code', '=', 'BASE'),
                 ('date_from', '>=', convert(from_date)),
                 ('date_to', '<=', to_date)]
        return len(bill_pool.search(cr, uid, query)) > 0
