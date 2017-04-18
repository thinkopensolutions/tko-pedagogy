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


class billing_details_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(billing_details_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'get_details_by_rule_category': self.get_details_by_rule_category,
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

    def get_details_by_rule_category(self, obj):
        billing_line = self.pool.get('pedagogy.billing.line')
        rule_cate_obj = self.pool.get('pedagogy.rule.category')

        def get_recursive_parent(rule_categories):
            if not rule_categories:
                return []
            if rule_categories[0].parent_id:
                rule_categories.insert(0, rule_categories[0].parent_id)
                get_recursive_parent(rule_categories)
            return rule_categories

        res = []
        result = {}
        ids = []

        for id in range(len(obj)):
            ids.append(obj[id].id)
        if ids:
            self.cr.execute('''SELECT pl.id, pl.billing_category_id FROM pedagogy_billing_line as pl \
                LEFT JOIN pedagogy_rule_category AS rc on (pl.billing_category_id = rc.id) \
                WHERE pl.id in %s \
                GROUP BY rc.billing_parent_id, pl.sequence, pl.id, pl.billing_category_id \
                ORDER BY pl.sequence, rc.billing_parent_id''', (tuple(ids),))
            for x in self.cr.fetchall():
                result.setdefault(x[1], [])
                result[x[1]].append(x[0])
            for key, value in result.iteritems():
                rule_categories = rule_cate_obj.browse(self.cr, self.uid, [key])
                parents = get_recursive_parent(rule_categories)
                category_total = 0
                for line in billing_line.browse(self.cr, self.uid, value):
                    category_total += line.total
                level = 0
                for parent in parents:
                    res.append({
                        'rule_category': parent.name,
                        'name': parent.name,
                        'code': parent.code,
                        'level': level,
                        'total': category_total,
                    })
                    level += 1
                for line in billing_line.browse(self.cr, self.uid, value):
                    res.append({
                        'rule_category': line.name,
                        'name': line.name,
                        'code': line.code,
                        'total': line.total,
                        'level': level
                    })
        return res


report_sxw.report_sxw('report.billing.details', 'pedagogy.billing', 'hr_payroll/report/report_billing_details.rml',
                      parser=billing_details_report)
