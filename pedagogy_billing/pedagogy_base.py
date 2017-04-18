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

from datetime import date

from osv import fields
from osv import osv

from pedagogy_enrollment import SCHEDULE_PAYS


class pedagogy_school_year(osv.osv):
    _inherit = 'pedagogy.school.year'

    def _get_current_school_year(self, cr, uid, context):
        date_today = date.today().strftime('%Y-%m-%d')
        year = self.search(cr, uid, [('date_start', '<=', date_today), ('date_end', '>=', date_today)])
        return self.browse(cr, uid, year)


class pedagogy_group(osv.osv):
    _name = 'pedagogy.group'
    _inherit = 'pedagogy.group'

    # Verify if dates are in current range of school year
    #     def _verify_dates(self, cr, uid, ids, context=None):
    #         school_year_pool = self.pool.get('pedagogy.school.year')
    #         year = self.pool.get('pedagogy.school.year')._get_current_school_year(cr, uid, context=None)
    #         if year and year[0]:
    #             for obj in self.browse(cr, uid, ids):
    #                 if obj.date_from and obj.date_to:
    #                     try:
    #                         assert obj.date_from >= year[0].date_start
    #                         assert obj.date_to <= year[0].date_end
    #                     except AssertionError:
    #                         raise osv.except_osv(_('Error'), _('The dates must be in range of School Year!'))
    #                 return True
    #         else:
    #             raise osv.except_osv(_('Error'), _('The dates must be in range of School Year!'))
    #         return False

    _columns = {
        'fee': fields.float('Fee', digits=(16, 2), help='Anual Fee of the student'),
        'struct_id': fields.many2one('pedagogy.billing.structure', 'Billing Structure'),
        'notes': fields.text('Description'),
        'date_from': fields.date('Date From'),
        'date_to': fields.date('Date To'),
        'schedule_pay': fields.selection(selection=SCHEDULE_PAYS, string='Scheduled Pay', select=True),
        'payment_term_id': fields.many2one('account.payment.term', 'Payment Terms',
                                           help="If you use payment terms, the due date will be computed automatically at the generation " \
                                                "of accounting entries. If you keep the payment term and the due date empty, it means direct payment. " \
                                                "The payment term may compute several due dates, for example 50% now, 50% in one month."),
    }

    #     _constraints = [(_verify_dates, 'Invalid Dates', ['date_from', 'date_to']),]

    def write_enroll(self, cr, uid, query, dict):
        billing_obj = self.pool.get('pedagogy.enrollment')
        bills = billing_obj.search(cr, uid, query)
        for bill in bills:
            billing_obj.write(cr, uid, [bill], dict)
        return True

    def write(self, cr, uid, ids, vals, context=None):
        billing_obj = self.pool.get('pedagogy.enrollment')
        if context is None:
            context = {}
        if type(ids).__name__ == 'list':
            for group in self.browse(cr, uid, ids):
                query = [('state', 'in', ('enrolled', 'pre-enrolled')),
                         ('class_year_id.class_id.group_id.id', '=', group.id)]
                if vals.has_key('date_from'):
                    query1 = query + [('contract_date_start', '!=', False),
                                      ('contract_date_start', '=', group.date_from)]
                    dict1 = {'contract_date_start': vals['date_from']}
                    self.write_enroll(cr, uid, query1, dict1)
                if vals.has_key('date_to'):
                    query2 = query + [('contract_date_end', '!=', False), ('contract_date_end', '=', group.date_to)]
                    dict2 = {'contract_date_end': vals['date_to']}
                    self.write_enroll(cr, uid, query2, dict2)
                if vals.has_key('fee'):
                    query3 = query + [('fee', '!=', False), ('fee', '=', group.fee)]
                    dict3 = {'fee': vals['fee']}
                    self.write_enroll(cr, uid, query3, dict3)
                if vals.has_key('struct_id'):
                    query4 = query + [('struct_id', '!=', False), ('struct_id', '=', group.struct_id.id)]
                    dict4 = {'struct_id': vals['struct_id']}
                    self.write_enroll(cr, uid, query4, dict4)
        return super(pedagogy_group, self).write(cr, uid, ids, vals, context=None)
