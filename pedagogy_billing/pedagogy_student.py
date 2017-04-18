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

from datetime import datetime

from osv import osv, fields


class pedagogy_student(osv.osv):
    _inherit = 'res.partner'

    def _get_invoicees(self, cr, uid, ids, field_name, arg=None, context=None):
        result = {}
        for partner in self.browse(cr, uid, ids):
            if partner.is_student:
                contract_ids = self.get_student_contract(cr, uid, partner.id, False, False,
                                                         datetime.now().strftime('%d-%m-%Y %H:%M:%S'), context)
                invoicees = list(set([line.invoicee_id for line in contract_obj.browse(cr, uid, contract_ids)]))
                result[partner.id] = [x.id for x in invoicees]
        return result

    columns = {
        'bill_ids': fields.one2many('hr.payslip', 'student_id', 'Bills'),
        'invoicee_ids': fields.function(_get_invoicees, method=True, type='one2many', relation='res.partner',
                                        string='Invoicees')
    }
