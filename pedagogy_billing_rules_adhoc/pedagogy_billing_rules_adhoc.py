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


# class hr_adhoc_salary_rule(osv.osv):
#    _name = 'pedagogy.rule'
#    _inherit = 'pedagogy.rule'
#    _columns = {
#        'billing_id': fields.many2many('pedagogy.billing', 'Billing (ad-hoc)', ondelete='cascade')
#    }
# hr_adhoc_salary_rule()

class pedagogy_billing(osv.osv):
    _inherit = 'pedagogy.billing'
    _columns = {
        'adhoc_rules': fields.many2many('pedagogy.rule', 'rule_adhoc_billing', 'rule_id', 'billing_id', 'Ad-hoc Rules',
                                        readonly=True, states={'draft': [('readonly', False)]}),
    }

    # to add our own ad-hoc rules
    def get_extra_rules(self, cr, uid, enrollment_ids, bill_id, context):
        parent = super(pedagogy_billing, self)
        rules = parent.get_extra_rules(cr, uid, enrollment_ids, bill_id, context)
        billing_obj = self.pool.get('pedagogy.billing')
        bill = billing_obj.browse(cr, uid, bill_id, context=context)
        rules.extend(bill.adhoc_rules)
        return rules

    def process_input_lines(self, cr, uid, input_line_ids):
        pool = self.pool.get('pedagogy.billing.input')
        codes = set()
        for state, id, vals in input_line_ids:
            if state == 0:
                codes.add(vals['code'])
            elif state == 4:
                [input] = pool.browse(cr, uid, [id])
                codes.add(input.code)
        return codes

    def update_input_lines(self, cr, uid, ids, enrollment_id, adhoc_rules, input_line_ids):
        if not enrollment_id:
            raise osv.except_osv(_('Error'), _('You must select an enrollment first'))
        rules_pool = self.pool.get('pedagogy.rule')
        codes = self.process_input_lines(cr, uid, input_line_ids)
        [[_, _, rule_ids]] = adhoc_rules
        for rule in rules_pool.browse(cr, uid, rule_ids):
            if rule.billing_input_ids:
                for input in rule.billing_input_ids:
                    if input.code not in codes:
                        input_line_ids.append((0, False, {
                            'name': input.name,
                            'code': input.code,
                            'enrollment_id': enrollment_id,
                        }))
        return {'value': {'input_line_ids': input_line_ids}}
