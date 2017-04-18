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

import tools
from osv import osv, fields


class pedagogy_billing_report(osv.osv):
    _name = 'pedagogy.billing.report'
    _description = 'Billing Report'
    _auto = False

    _columns = {
        'name': fields.char('Description', size=120, required=True),
        'number': fields.char('Reference', size=64, required=True),
        'date_from': fields.date('Date From', required=True),
        'date_to': fields.date('Date To', required=True),
        'year': fields.char('Year', size=4, readonly=True),
        'month': fields.selection([('01', 'January'), ('02', 'February'), ('03', 'March'), ('04', 'April'),
                                   ('05', 'May'), ('06', 'June'), ('07', 'July'), ('08', 'August'), ('09', 'September'),
                                   ('10', 'October'), ('11', 'November'), ('12', 'December')], 'Month', readonly=True),
        'day': fields.char('Day', size=128, readonly=True),
        'student_id': fields.many2one('res.partner', 'Student', required=True),
        'employee_id': fields.many2one('hr.employee', 'Employee', required=True),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('confirm', 'Confirmed'),
            ('paid', 'Paid'),
            ('cancel', 'Canceled'),
            ('invoiced', 'Invoiced')],
            'State', required=True),
        'invoicee_id': fields.many2one('res.partner', 'Invoicee', required=True),
        'enrollment_id': fields.many2one('pedagogy.enrollment', 'Enrollment', required=True),
        'struct_id': fields.many2one('pedagogy.billing.structure', 'Structure', required=True),
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'paid': fields.boolean('Made Payment Order ? ', required=True),
        'note': fields.text('Description', required=True),
        'credit_note': fields.boolean('Credit Note', required=True),
        'run_id': fields.many2one('pedagogy.billing.run', 'Billing Batch'),
        'amount_total': fields.float('Amount Total'),
    }

    def init(self, cr):
        tools.sql.drop_view_if_exists(cr, 'pedagogy_billing_report')
        cr.execute('''
            CREATE or REPLACE view pedagogy_billing_report as (
                    SELECT  
                        pb.id as id
                        ,pb.name
                        ,pb.number
                        ,pb.date_from
                        ,pb.date_to
                        ,pb.student_id
                        ,pb.employee_id
                        ,pb.state
                        ,pb.invoicee_id
                        ,pb.enrollment_id
                        ,pb.struct_id
                        ,pb.company_id
                        ,pb.paid
                        ,pb.note
                        ,pb.credit_note
                        ,pb.run_id
                        ,to_char(pb.date_from, 'YYYY') as year
                        ,to_char(pb.date_from, 'MM') as month
                        ,pb.amount_total
                    FROM
                        pedagogy_billing pb
                    )
        ''')
