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

import pooler
from osv import osv, fields
from tools.translate import _


class pedagogy_billing_account_invoice_create(osv.osv_memory):
    '''
    This wizard will agregate billings in a single invoice per invoicee if group is selected
    '''

    _name = 'pedagogy.billing.account.invoice.create'
    _description = 'Pedagogy Billing Account Invoice Create'

    _columns = {
        'group_by_invoicee': fields.boolean('Group By Envoicee')
    }

    def invoice_create(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        pool_obj = pooler.get_pool(cr.dbname)
        group = pool_obj.get('pedagogy.billing.account.invoice.create').browse(cr, uid, ids[0]).group_by_invoicee
        pedagogy_billing_obj = pool_obj.get('pedagogy.billing')
        data_billing = pedagogy_billing_obj.read(cr, uid, context['active_ids'], ['state', 'invoicee_id'],
                                                 context=context)
        if not group:
            for record in data_billing:
                if record['state'] != 'confirm':
                    raise osv.except_osv(_('Error !'), _('Only billings in state Confirmed can be invoiced.'))
                pedagogy_billing_obj.invoice(cr, uid, [record['id']])
        else:
            grouped_billings = {}
            for record in data_billing:
                if record['state'] != 'confirm':
                    raise osv.except_osv(_('Error !'), _('Only billings in state Confirmed can be invoiced.'))
                # group by invoicee
                if not grouped_billings.has_key(record['invoicee_id']):
                    grouped_billings[record['invoicee_id']] = []
                grouped_billings[record['invoicee_id']].append(record['id'])
            for group in grouped_billings:
                pedagogy_billing_obj.invoice_in_group(cr, uid, grouped_billings[group])
        return {
            'name': _('Customer Invoices'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.invoice',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'domain': '[]',
        }


class pedagogy_billing_run_account_invoice_create(osv.osv_memory):
    '''
    This wizard will agregate billings in a single invoice per invoicee if group is selected
    '''

    _name = 'pedagogy.billing.run.account.invoice.create'
    _description = 'Pedagogy Billing Run Account Invoice Create'

    _columns = {
        'group_by_invoicee': fields.boolean('Group By Envoicee')
    }

    def invoice_create(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        pool_obj = pooler.get_pool(cr.dbname)
        group = pool_obj.get('pedagogy.billing.run.account.invoice.create').browse(cr, uid, ids[0]).group_by_invoicee
        pedagogy_billing_obj = pool_obj.get('pedagogy.billing')
        data_billing = []
        for line in pool_obj.get('pedagogy.billing.run').read(cr, uid, context['active_ids'], ['state', 'bill_ids'],
                                                              context=context):
            if line['state'] != 'close':
                raise osv.except_osv(_('Error !'), _('Only billings runs in state Done can be invoiced.'))
            for bill in line['bill_ids']:
                data_billing.append(pedagogy_billing_obj.read(cr, uid, bill, ['state', 'invoicee_id'], context=context))
        if not group:
            for record in data_billing:
                if record['state'] != 'confirm':
                    raise osv.except_osv(_('Error !'), _('Only billings in state Confirmed can be invoiced.'))
                pedagogy_billing_obj.invoice(cr, uid, [record['id']])
        else:
            grouped_billings = {}
            for record in data_billing:
                if record['state'] != 'confirm':
                    raise osv.except_osv(_('Error !'), _('Only billings in state Confirmed can be invoiced.'))
                # group by invoicee
                if not grouped_billings.has_key(record['invoicee_id']):
                    grouped_billings[record['invoicee_id']] = []
                grouped_billings[record['invoicee_id']].append(record['id'])
            for group in grouped_billings:
                pedagogy_billing_obj.invoice_in_group(cr, uid, grouped_billings[group])
        return {
            'name': _('Customer Invoices'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.invoice',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'domain': '[]',
        }
