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


class billing_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(billing_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'get_billing_lines': self.get_billing_lines,
            'adr_get': self._adr_get,
            'calculate_total': self._calculate_total,
            'get_bank_info': self.get_bank_info,
        })

    def get_bank_info(self):
        res = {}
        banks = self.objects[0].company_id.bank_ids
        if banks:
            res['name'] = banks[0].bank_name
            res['nib'] = banks[0].acc_number
        return res

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

    def _calculate_total(self, obj):
        billing_line = self.pool.get('pedagogy.billing.line')
        res = {}
        ids = []
        total = 0.0
        net = 0.0
        for id in range(len(obj)):
            if obj[id].code == 'NET':
                total = obj[id].total
        res['total'] = total
        return res

    def get_billing_lines(self, obj):
        billing_line = self.pool.get('pedagogy.billing.line')
        res = []
        ids = []
        for id in range(len(obj)):
            if obj[id].appears_on_payslip == True and obj[id].code not in ('NET', 'PRS'):
                ids.append(obj[id].id)
        if ids:
            res = billing_line.browse(self.cr, self.uid, ids)
        return res


report_sxw.report_sxw('report.billing', 'pedagogy.billing', 'hr_payroll/report/report_billing.rml',
                      parser=billing_report)
