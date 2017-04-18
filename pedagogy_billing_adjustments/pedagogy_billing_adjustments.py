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

from openerp.osv import fields
from openerp.osv import osv


class pedagogy_billing_adjustment(osv.osv):
    _name = 'pedagogy.billing.adjustment'
    _description = 'Pedagogy Billing Adjustment'
    _columns = {
        'code': fields.char('Code', size=18, required=True),
        'name': fields.char('Name', size=128, required=True),
        'student_id': fields.many2one('res.partner', 'Student', required=True),
        'discount_percentage': fields.float('Discount Percentage', digits=(16, 2), required=True,
                                            help='Discount for student'),
        'partner_id': fields.many2one('res.partner', 'Partner'),
    }


class pedagogy_billing(osv.osv):
    _inherit = 'pedagogy.billing'

    def get_adjustment(self, cr, uid, code, student_id):
        cr.execute('select discount_percentage\
                        from pedagogy_billing_adjustment\
                        where student_id = %s and code = %s', (student_id, code))
        res = cr.fetchone()
        return res and res[0] or 0.0
