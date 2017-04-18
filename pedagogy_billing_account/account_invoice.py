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

from osv import osv, fields


class account_invoice(osv.osv):
    _inherit = 'account.invoice'

    def confirm_paid(self, cr, uid, ids, context=None):
        res = super(account_invoice, self).confirm_paid(cr, uid, ids, context)
        billing_obj = self.pool.get('pedagogy.billing')
        for line in self.browse(cr, uid, ids):
            if line.billing_ids:
                billing_ids = [x.id for x in line.billing_ids]
                billing_obj.write(cr, uid, billing_ids, {'state': 'paid'})
        return True

    def action_cancel(self, cr, uid, ids, *args):
        res = super(account_invoice, self).action_cancel(cr, uid, ids, *args)
        billing_obj = self.pool.get('pedagogy.billing')
        for line in self.browse(cr, uid, ids):
            if line.billing_ids:
                billing_ids = [x.id for x in line.billing_ids]
                billing_obj.write(cr, uid, billing_ids, {'state': 'cancel'})
        return True

    _columns = {
        'billing_ids': fields.one2many('pedagogy.billing', 'invoice_id', 'Billings'),
    }
