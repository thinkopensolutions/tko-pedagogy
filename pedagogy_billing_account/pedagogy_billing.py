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

import netsvc
from osv import osv, fields
from tools.translate import _


class pedagogy_billing_line(osv.osv):
    _name = 'pedagogy.billing.line'
    _inherit = 'pedagogy.billing.line'

    def _get_product(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            if line.billing_rule_id and line.billing_rule_id.product_id:
                res[line.id] = line.billing_rule_id.product_id.id
            elif line.product_no_rule:
                res[line.id] = line.product_no_rule.id
        return res

    def _write_product(self, cr, uid, id, field_name, field_value, arg, context=None):
        for line in self.browse(cr, uid, [id], context=context):
            if line.billing_rule_id:
                pool = self.pool.get('pedagogy.rule')
                pool.write(cr, uid, [line.billing_rule_id.id], {'product_id': field_value}, context=context)
            else:
                self.write(cr, uid, [id], {'product_no_rule': field_value}, context=context)

    _columns = {
        'display_product': fields.function(_get_product, fnct_inv=_write_product, method=True, type='many2one',
                                           relation='product.product', string='Product'),
        'product_no_rule': fields.many2one('product.product', 'Rule-less Product'),
    }


class pedagogy_billing_invoice(osv.osv):
    _name = 'pedagogy.billing'
    _inherit = 'pedagogy.billing'
    _description = 'Pedagogy Billing'
    _rec_name = 'number'

    _columns = {
        'state': fields.selection([
            ('draft', 'Draft'),
            ('confirm', 'Confirmed'),
            ('paid', 'Paid'),
            ('cancel', 'Canceled'),
            ('invoiced', 'Invoiced')
        ],
            'State', select=True, readonly=True, help='* When the billing is created the state is \'Draft\'.\
                                        \n* If the billing is under verification, the state is \'Waiting\'. \
                                        \n* If the billing is confirmed then state is set to \'Confirmed\'.\
                                        \n* If the billing is invoiced then state is set to \'Invoiced\'.\
                                        \n* When user cancel the invoice associated the state is \'Canceled\'.\
                                        \n* When user pay the invoice associated to the billin  the state is \'Canceled\'.\
                                        \n* When user cancel billing the state is \'Canceled\'.'),
        'invoice_id': fields.many2one('account.invoice', 'Invoice', readonly=True),
        'payments_ids': fields.related('invoice_id', 'payment_ids', type='one2many', relation='account.move.line',
                                       string='Payments', readonly=True),
    }

    def copy(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        company_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id
        default.update({
            'line_ids': [],
            'move_ids': [],
            'move_line_ids': [],
            'company_id': company_id,
            'period_id': False,
            'basic_before_leaves': 0.0,
            'basic_amount': 0.0,
            'invoice_id': False,
        })
        return super(pedagogy_billing_invoice, self).copy(cr, uid, id, default, context=context)

    def unlink(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        billings = self.read(cr, uid, ids, ['state'], context=context)
        unlink_ids = []
        for t in billings:
            if t['state'] in ('draft'):
                unlink_ids.append(t['id'])
            else:
                raise osv.except_osv(_('Invalid action !'), _('Cannot delete bill(s) that are not in state draft!'))
        osv.osv.unlink(self, cr, uid, unlink_ids, context=context)
        return True

    def make_comment(self, student_ids):
        def format(student):
            val = [student.name]
            if student.vat:
                val.append(u'({0}: {1})'.format(_('VAT'), student.vat))
            return u' '.join(val)

        try:
            students = map(format, student_ids)
            res = (_(u'Relativo aos estudantes:'), u', '.join(students))
        except TypeError:  # student_ids is a single student
            res = (_(u'Relativo ao estudante:'), format(student_ids))
        return u' '.join(res)

    def _get_unlink_categories(self, cr, uid, ids, context=None):
        """ Method to get ignored billing rules categories from invoice in PRS rule
        """
        res = ['NET']
        rules_obj = self.pool.get('pedagogy.rule')
        prs_rule_id = rules_obj.search(cr, uid, [('code', '=', 'PRS')], order='id', limit=1)
        if prs_rule_id and prs_rule_id[0]:
            prs_rule = rules_obj.browse(cr, uid, prs_rule_id[0])
            categories_list = prs_rule.amount_python_compute.split('categories.')
            categories = [cat.replace('+', '').strip() for cat in categories_list if cat.find('result') < 0]
            if categories:
                res += categories
        return res

    def invoice(self, cr, uid, ids, context=None):
        res = False
        invoice_obj = self.pool.get('account.invoice')
        property_obj = self.pool.get('ir.property')
        sequence_obj = self.pool.get('ir.sequence')
        product_obj = self.pool.get('product.product')
        analytic_journal_obj = self.pool.get('account.analytic.journal')
        account_journal = self.pool.get('account.journal')

        for bill in self.browse(cr, uid, ids):
            company_id = bill.company_id.id
            lines = []
            unlink_categories = self._get_unlink_categories(cr, uid, ids, context)
            for l in bill.line_ids:
                # Be sure not to create lines with amount equal to zero or negative
                # or pedagogy rule for base amount and net
                if l.total == 0.00 or l.total < 0 or l.billing_category_id.code in unlink_categories:
                    continue
                # Be sure to have a product associated to a billing rule
                if l.billing_rule_id.product_id:
                    product = l.billing_rule_id.product_id
                elif l.product_no_rule:
                    product = l.product_no_rule
                else:
                    raise osv.except_osv(_('Error !'), _('Not all lines have products!'))
                tax_id = []
                fpos_obj = self.pool.get('account.fiscal.position')
                fpos = False
                # Get account_id from product
                acc = product.product_tmpl_id.property_account_income.id
                if not acc:
                    acc = product.categ_id.property_account_income_categ.id
                acc = fpos_obj.map_account(cr, uid, fpos, acc)
                if not acc:
                    raise osv.except_osv(_('Error !'),
                                         _('Please configure the account income of product, `property_account_income`'))
                taxes = product.taxes_id and product.taxes_id or (
                acc and self.pool.get('account.account').browse(cr, uid, acc, context=context).tax_ids or False)
                tax_id = fpos_obj.map_tax(cr, uid, fpos, taxes)
                lines.append((0, False, {
                    'name': l.name,
                    'account_id': acc,
                    'price_unit': l.amount,
                    'quantity': l.quantity,
                    'uos_id': product and product.uom_id.id or False,
                    'product_id': product and product.id or False,
                    'invoice_line_tax_id': tax_id and [(6, 0, tax_id)] or False,
                    'account_analytic_id': False,
                }))
            # partner address
            res = self.pool.get('res.partner').address_get(cr, uid, [bill.invoicee_id.id], ['contact', 'invoice'])
            contact_addr_id = res['contact']
            invoice_addr_id = res['invoice']
            p = self.pool.get('res.partner').browse(cr, uid, bill.invoicee_id.id)

            if company_id:
                if p.property_account_receivable.company_id.id != company_id:
                    property_obj = self.pool.get('ir.property')
                    rec_pro_id = property_obj.search(cr, uid, [('name', '=', 'property_account_receivable'),
                                                               ('res_id', '=', 'res.partner,' + str(partner_id) + ''),
                                                               ('company_id', '=', company_id)])
                    # pay_pro_id = property_obj.search(cr,uid,[('name','=','property_account_payable'),('res_id','=','res.partner,'+str(partner_id)+''),('company_id','=',company_id)])
                    if not rec_pro_id:
                        rec_pro_id = property_obj.search(cr, uid, [('name', '=', 'property_account_receivable'),
                                                                   ('company_id', '=', company_id)])
                        #     if not pay_pro_id:
                        #         pay_pro_id = property_obj.search(cr,uid,[('name','=','property_account_payable'),('company_id','=',company_id)])
                    rec_line_data = property_obj.read(cr, uid, rec_pro_id, ['name', 'value_reference', 'res_id'])
                    #    pay_line_data = property_obj.read(cr,uid,pay_pro_id,['name','value_reference','res_id'])
                    rec_res_id = rec_line_data and rec_line_data[0].get('value_reference', False) and int(
                        rec_line_data[0]['value_reference'].split(',')[1]) or False
                    #    pay_res_id = pay_line_data and pay_line_data[0].get('value_reference',False) and int(pay_line_data[0]['value_reference'].split(',')[1]) or False
                    if not rec_res_id:
                        raise osv.except_osv(_('Configuration Error !'),
                                             _('Can not find account chart for this company, Please Create account.'))
                    account_obj = self.pool.get('account.account')
                    rec_obj_acc = account_obj.browse(cr, uid, [rec_res_id])
                    #  pay_obj_acc = account_obj.browse(cr, uid, [pay_res_id])
                    p.property_account_receivable = rec_obj_acc[0]
                    # p.property_account_payable = pay_obj_acc[0]
                    acc_id = p.property_account_receivable.id
                else:
                    acc_id = p.property_account_receivable.id
            payment_term_id = bill.payment_term_id.id
            inv = {
                'name': bill.name,
                'account_id': acc_id,
                'type': 'out_invoice',
                'partner_id': bill.invoicee_id.id,
                'address_invoice_id': invoice_addr_id,
                'address_contact_id': contact_addr_id,
                'company_id': company_id,
                'origin': bill.name,
                'invoice_line': lines,
                'currency_id': p.company_id.currency_id.id,
                'payment_term': payment_term_id,
                'fiscal_position': p.property_account_position and p.property_account_position.id or False,
                'comment': self.make_comment(bill.student_id),
                'exemption_reason': u'Isento Artigo 9.º do CIVA',
                'force_open': True
            }
            if payment_term_id:
                to_update = invoice_obj.onchange_payment_term_date_invoice(cr, uid, [], payment_term_id, None)
                if to_update:
                    inv.update(to_update['value'])
            inv_id = invoice_obj.create(cr, uid, inv, {'type': 'out_invoice'})
            invoice_obj.button_compute(cr, uid, [inv_id], {'type': 'out_invoice'}, set_total=True)
            # force state transition to open
            self.write(cr, uid, [bill.id], {'invoice_id': inv_id, 'state': 'invoiced'})
            wf_service = netsvc.LocalService('workflow')
            wf_service.trg_validate(uid, 'account.invoice', inv_id, 'invoice_open', cr)
            res = inv_id
            mod_obj = self.pool.get('ir.model.data')
            views = mod_obj.get_object_reference(cr, uid, 'account', 'invoice_form')
        return {
            'name': _('Customer Invoices'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': [views and views[1] or False],
            'res_model': 'account.invoice',
            'context': "{'type':'out_invoice', 'journal_type': 'sale'}",
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'res_id': res or False,
        }

    def invoice_in_group(self, cr, uid, ids, context=None):
        res = False
        invoice_obj = self.pool.get('account.invoice')
        property_obj = self.pool.get('ir.property')
        sequence_obj = self.pool.get('ir.sequence')
        product_obj = self.pool.get('product.product')
        analytic_journal_obj = self.pool.get('account.analytic.journal')
        account_journal = self.pool.get('account.journal')
        lines = []
        students = set()

        # create lines
        for bill in self.browse(cr, uid, ids):
            students.add(bill.student_id)
            company_id = bill.company_id.id
            # make invoice line with product type = title for map student bill lines
            lines.append((0, False, {
                'state': 'title',
                'name': bill.student_id.name + u'-' + bill.class_year_id.name,
            }))
            for l in bill.line_ids:
                # Be sure not to create lines with amount equal to zero or negative
                if l.amount == 0.00 or l.amount < 0 or l.billing_category_id.code == 'BASE' or l.billing_category_id.code == 'NET' \
                        or l.billing_category_id.code == 'ACM':
                    continue
                # Be sure to have a product associated to a billing rule
                if l.billing_rule_id.product_id:
                    product = l.billing_rule_id.product_id
                elif l.product_no_rule:
                    product = l.product_no_rule
                else:
                    raise osv.except_osv(_('Error !'),
                                         _('Create a product to billing rule: %s' % l.billing_rule_id.name))
                tax_id = []
                fpos_obj = self.pool.get('account.fiscal.position')
                fpos = False
                # Get account_id from product
                acc = product.product_tmpl_id.property_account_income.id
                if not acc:
                    acc = product.categ_id.property_account_income_categ.id
                acc = fpos_obj.map_account(cr, uid, fpos, acc)
                if not acc:
                    raise osv.except_osv(_('Error !'),
                                         _('Please configure the account income of product, `property_account_income`'))
                taxes = product.taxes_id and product.taxes_id or (
                acc and self.pool.get('account.account').browse(cr, uid, acc, context=context).tax_ids or False)
                tax_id = fpos_obj.map_tax(cr, uid, fpos, taxes)
                lines.append((0, False, {
                    'name': l.name,
                    'account_id': acc,
                    'price_unit': l.amount,
                    'quantity': l.quantity,
                    'uos_id': product and product.uom_id.id or False,
                    'product_id': product and product.id or False,
                    'invoice_line_tax_id': tax_id and [(6, 0, tax_id)] or False,
                    'account_analytic_id': False,
                }))
            # partner address
            res = self.pool.get('res.partner').address_get(cr, uid, [bill.invoicee_id.id], ['contact', 'invoice'])
            contact_addr_id = res['contact']
            invoice_addr_id = res['invoice']
            p = self.pool.get('res.partner').browse(cr, uid, bill.invoicee_id.id)

            if company_id:
                if p.property_account_receivable.company_id.id != company_id:
                    property_obj = self.pool.get('ir.property')
                    rec_pro_id = property_obj.search(cr, uid, [('name', '=', 'property_account_receivable'),
                                                               ('res_id', '=', 'res.partner,' + str(partner_id) + ''),
                                                               ('company_id', '=', company_id)])
                    # pay_pro_id = property_obj.search(cr,uid,[('name','=','property_account_payable'),('res_id','=','res.partner,'+str(partner_id)+''),('company_id','=',company_id)])
                    if not rec_pro_id:
                        rec_pro_id = property_obj.search(cr, uid, [('name', '=', 'property_account_receivable'),
                                                                   ('company_id', '=', company_id)])
                        #     if not pay_pro_id:
                        #         pay_pro_id = property_obj.search(cr,uid,[('name','=','property_account_payable'),('company_id','=',company_id)])
                    rec_line_data = property_obj.read(cr, uid, rec_pro_id, ['name', 'value_reference', 'res_id'])
                    #    pay_line_data = property_obj.read(cr,uid,pay_pro_id,['name','value_reference','res_id'])
                    rec_res_id = rec_line_data and rec_line_data[0].get('value_reference', False) and int(
                        rec_line_data[0]['value_reference'].split(',')[1]) or False
                    #    pay_res_id = pay_line_data and pay_line_data[0].get('value_reference',False) and int(pay_line_data[0]['value_reference'].split(',')[1]) or False
                    if not rec_res_id:
                        raise osv.except_osv(_('Configuration Error !'),
                                             _('Can not find account chart for this company, Please Create account.'))
                    account_obj = self.pool.get('account.account')
                    rec_obj_acc = account_obj.browse(cr, uid, [rec_res_id])
                    #  pay_obj_acc = account_obj.browse(cr, uid, [pay_res_id])
                    p.property_account_receivable = rec_obj_acc[0]
                    # p.property_account_payable = pay_obj_acc[0]
                    acc_id = p.property_account_receivable.id
                else:
                    acc_id = p.property_account_receivable.id
        payment_term_id = bill.payment_term_id.id
        # create invoice
        name = str([x.name for x in self.browse(cr, uid, ids)]).replace('u''', '').strip('[]')
        inv = {
            'name': name,
            #   'reference': sequence_obj.get(cr, uid, 'hr.expense.invoice'),
            'account_id': acc_id,
            'type': 'out_invoice',
            'partner_id': bill.invoicee_id.id,
            'address_invoice_id': invoice_addr_id,
            'address_contact_id': contact_addr_id,
            'company_id': company_id,
            'origin': name,
            'invoice_line': lines,
            'currency_id': p.company_id.currency_id.id,
            'payment_term': bill.payment_term_id.id,
            'fiscal_position': p.property_account_position and p.property_account_position.id or False,
            'comment': self.make_comment(bill.student_id),
            'exemption_reason': u'Isento Artigo 9.º do CIVA',
            'force_open': True
        }
        if payment_term_id:
            to_update = invoice_obj.onchange_payment_term_date_invoice(cr, uid, [], payment_term_id, None)
            if to_update:
                inv.update(to_update['value'])
        inv_id = invoice_obj.create(cr, uid, inv, {'type': 'out_invoice'})
        invoice_obj.button_compute(cr, uid, [inv_id], {'type': 'out_invoice'}, set_total=True)
        # force state transition to open
        wf_service = netsvc.LocalService('workflow')
        wf_service.trg_validate(uid, 'account.invoice', inv_id, 'invoice_open', cr)
        self.write(cr, uid, ids, {'invoice_id': inv_id, 'state': 'invoiced'})
        res = inv_id
        mod_obj = self.pool.get('ir.model.data')
        views = mod_obj.get_object_reference(cr, uid, 'account', 'invoice_form')
        return {
            'name': _('Customer Invoices'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': [views and views[1] or False],
            'res_model': 'account.invoice',
            'context': "{'type':'out_invoice', 'journal_type': 'sale'}",
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'res_id': res or False,
        }


class pedagogy_billing_run(osv.osv):
    _name = 'pedagogy.billing.run'
    _inherit = 'pedagogy.billing.run'

    def copy(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        company_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id
        default.update({
            'company_id': company_id,
            'bill_ids': False,
        })
        return super(pedagogy_billing_run, self).copy(cr, uid, id, default, context=context)


class pedagogy_rule_with_product(osv.osv):
    _name = 'pedagogy.rule'
    _inherit = 'pedagogy.rule'

    _columns = {
        'product_id': fields.many2one('product.product', 'Product', ondelete='cascade'),
    }

    # Creating the product associated to billing rule
    def create(self, cr, uid, vals, context=None):
        product_obj = self.pool.get('product.product')
        new_id = super(pedagogy_rule_with_product, self).create(cr, uid, vals, context)
        rule = self.browse(cr, uid, new_id)
        if rule and not rule.product_id:
            product = {
                'name': rule.name,
                'default_code': rule.code,
                'type': 'service',
                'sale_ok': True,
                'purchase_ok': False,
            }
            product_id = product_obj.create(cr, uid, product, context)
            if product_id:
                self.write(cr, uid, [new_id], {'product_id': product_id})
        return new_id

    # If modify name or code of rule, modify also in product
    def write(self, cr, uid, ids, vals, context=None):
        product_obj = self.pool.get('product.product')
        res = super(pedagogy_rule_with_product, self).write(cr, uid, ids, vals, context=context)
        for rule in self.browse(cr, uid, ids):
            if rule.product_id:
                if vals.has_key('name'):
                    product_obj.write(cr, uid, [rule.product_id.id], {'name': vals['name']})
                if vals.has_key('code'):
                    product_obj.write(cr, uid, [rule.product_id.id], {'default_code': vals['code']})
        return res
