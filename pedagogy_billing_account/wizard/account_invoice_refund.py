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

from osv import fields, osv


class account_invoice_refund(osv.osv_memory):
    _inherit = 'account.invoice.refund'

    _columns = {
        'filter_refund': fields.selection([('refund', 'Create a draft Refund'),
                                           ('cancel', 'Cancel: refund invoice and reconcile'),
                                           ], 'Refund Method', required=True,
                                          help='Refund invoice base on this type. You can not Modify and Cancel if the invoice is already reconciled'),
    }

    def compute_refund(self, cr, uid, ids, mode='refund', context=None):
        result = super(account_invoice_refund, self).compute_refund(cr, uid, ids, mode, context)
        pedagogy_billing_obj = self.pool.get('pedagogy.billing')
        inv_obj = self.pool.get('account.invoice')
        if mode == 'cancel':
            for form in self.browse(cr, uid, ids, context=context):
                for inv in inv_obj.browse(cr, uid, context.get('active_ids'), context=context):
                    if inv.billing_ids:
                        for billing in inv.billing_ids:
                            pedagogy_billing_obj.write(cr, uid, [billing.id], {'credit_note': True})
        return result
