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

from report import report_sxw


class invoicees_billing(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(invoicees_billing, self).__init__(cr, uid, name, context=context)
        self.init_bal_sum = 0.0
        self.localcontext.update({
            'lines': self.lines,
            'get_date_from': self.get_date_from,
            'get_date_to': self.get_date_to,
            'get_students': self.get_students,
            'student_total': self.student_total,
            'full_total': self.full_total,
            'billings': self.billings,
            'get_bank_info': self.get_bank_info,
            'adr_get': self._adr_get,
        })

    def _adr_get(self, partner):
        res = []
        if not partner:
            return False
        res_partner = self.pool.get('res.partner')
        address_ids = res_partner.address_get(self.cr, self.uid, [partner.id], ['default'])
        adr_id = address_ids and address_ids['default'] or False
        if adr_id:
            adr = res_partner.browse(self.cr, self.uid, [adr_id])[0]
            return adr
        return False

    def get_bank_info(self):
        res = {}
        banks = self.objects[0].company_id.bank_ids
        if banks:
            res['name'] = banks[0].bank_name
            res['nib'] = banks[0].acc_number
        return res

    def get_date_from(self):
        return self.billings[0].date_from

    def get_date_to(self):
        return self.billings[0].date_to

    def get_invoicees(self, billings):
        invoicees = set(billing.invoicee_id for billing in billings)
        return list(invoicees)

    def full_total(self, invoicee):
        total = 0.0
        for billing in self.billings:
            if billing.invoicee_id == invoicee:
                for line in billing.line_ids:
                    if line.code == 'NET':
                        total += line.total
        return total

    def get_students(self, invoicee):
        students = set()
        for billing in self.billings:
            if billing.invoicee_id == invoicee:
                students.add(billing.student_id)
        return students

    def student_total(self, invoicee, student):
        total = 0.0
        for billing in self.billings:
            if billing.invoicee_id == invoicee and billing.student_id == student:
                for line in billing.line_ids:
                    if line.code == 'NET':
                        total += line.total
        return total

    def set_context(self, objects, data, ids, report_type=None):
        billing_pool = self.pool.get('pedagogy.billing')
        invoicee_pool = self.pool.get('res.partner')
        chosen_billings = billing_pool.browse(self.cr, self.uid, ids)
        invoicees = self.get_invoicees(chosen_billings)
        invoicees_ids = [i.id for i in invoicees]
        dates = [b.date_from for b in chosen_billings]
        query = [('invoicee_id', 'in', invoicees_ids), ('date_from', 'in', dates), ('state', 'not in', ['cancel'])]
        all_billings_ids = billing_pool.search(self.cr, self.uid, query)
        self.billings = billing_pool.browse(self.cr, self.uid, all_billings_ids)
        return super(invoicees_billing, self).set_context(invoicees, data, [], report_type)

    def billings(self, invoicee, student):
        res = []
        billing_list = []
        for billing in self.billings:
            if billing.invoicee_id == invoicee and billing.student_id == student:
                billing_list.append(billing)
        return billing_list

    def lines(self, billing):
        res = []
        for line in billing.line_ids:
            if line.appears_on_payslip == True and line.code not in ('NET', 'PRS'):
                res.append({'class_year': billing.class_year_id.name,
                            'ref': billing.number,
                            'code': line.code,
                            'name': line.name,
                            'quantity': line.quantity,
                            'rate': line.rate,
                            'amount': line.amount,
                            'total': line.total})
        return res


report_sxw.report_sxw('report.invoicees_billing', 'pedagogy.billing',
                      'pedagogy_billing/report/invoicees_billing.rml', parser=invoicees_billing)
