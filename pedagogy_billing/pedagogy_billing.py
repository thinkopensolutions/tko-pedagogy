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

import time
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

import decimal_precision as dp
import netsvc
import tools
from osv import osv, fields
from tools.safe_eval import safe_eval as eval
from tools.translate import _

DATE_FORMAT = '%Y-%m-%d'


class pedagogy_rule(osv.osv):
    _name = 'pedagogy.rule'
    _inherit = 'hr.salary.rule'

    _columns = {
        'billing_category_id': fields.many2one('pedagogy.rule.category', 'Category', required=True),
        'parent_billing_rule_id': fields.many2one('pedagogy.rule', 'Parent Salary Rule', select=True),
        'billing_child_ids': fields.one2many('pedagogy.rule', 'parent_billing_rule_id', 'Child Billing Rule'),
        'category_id': fields.many2one('hr.salary.rule.category', 'Category'),
        'billing_input_ids': fields.one2many('pedagogy.rule.input', 'billing_input_id', 'Inputs'),
        'input_ids': fields.one2many('hr.rule.input', 'input_id', 'Inputs'),
    }

    _defaults = {
        'amount_python_compute': '''
# Available variables:
#----------------------
# student: res.partner object
# enrollment: pedagogy.enrollment object
# rules: object containing the rules code (previously computed)
# categories: object containing the computed salary rule categories (sum of amount of all rules belonging to that category).
# inputs: object containing the computed inputs.

# Note: returned value have to be set in the variable 'result'

result = enrollment.class_year_id.fee''',
        'condition_python':
            '''
            result = rules.NET > categories.NET * 0.10''',
    }

    def _recursive_search_of_rules(self, cr, uid, rule_ids, context=None):
        '''
        @param rule_ids: list of browse record
        @return: returns a list of tuple (id, sequence) which are all the children of the passed rule_ids
        '''
        children_rules = []
        for rule in rule_ids:
            if rule.billing_child_ids:
                children_rules += self._recursive_search_of_rules(cr, uid, rule.billing_child_ids, context=context)
        return [(r.id, r.sequence) for r in rule_ids] + children_rules

        # TODO should add some checks on the type of result (should be float)

    def billing_compute_rule(self, cr, uid, rule_id, localdict, context=None):
        '''
        :param rule_id: id of rule to compute
        :param localdict: dictionary containing the environement in which to compute the rule
        :return: returns a tuple build as the base/amount computed, the quantity and the rate 
        :rtype: (float, float, float)
        '''
        rule = self.browse(cr, uid, rule_id, context=context)
        if rule.amount_select == 'fix':
            try:
                return rule.amount_fix, eval(rule.quantity, localdict), 100.0
            except:
                raise osv.except_osv(_('Error'),
                                     _('Wrong quantity defined for salary rule %s (%s)') % (rule.name, rule.code))
        elif rule.amount_select == 'percentage':
            try:
                return eval(rule.amount_percentage_base, localdict), eval(rule.quantity,
                                                                          localdict), rule.amount_percentage
            except:
                raise osv.except_osv(_('Error'),
                                     _('Wrong percentage base or quantity defined for salary rule %s (%s)') % (
                                     rule.name, rule.code))
        else:
            try:
                eval(rule.amount_python_compute, localdict, mode='exec', nocopy=True)
                return localdict['result'], 'result_qty' in localdict and localdict[
                    'result_qty'] or 1.0, 'result_rate' in localdict and localdict['result_rate'] or 100.0
            except:
                raise osv.except_osv(_('Error'),
                                     _('Wrong python code defined for salary rule %s (%s) ') % (rule.name, rule.code))

    def billing_satisfy_condition(self, cr, uid, rule_id, localdict, context=None):
        '''
        @param rule_id: id of hr.salary.rule to be tested
        @param contract_id: id of hr.contract to be tested
        @return: returns True if the given rule match the condition for the given contract. Return False otherwise.
        '''
        rule = self.browse(cr, uid, rule_id, context=context)

        if rule.condition_select == 'none':
            return True
        elif rule.condition_select == 'range':
            try:
                result = eval(rule.condition_range, localdict)
                return rule.condition_range_min <= result and result <= rule.condition_range_max or False
            except:
                raise osv.except_osv(_('Error'), _('Wrong range condition defined for salary rule %s (%s)') % (
                rule.name, rule.code))
        else:  # python code
            try:
                eval(rule.condition_python, localdict, mode='exec', nocopy=True)
                return 'result' in localdict and localdict['result'] or False
            except:
                raise osv.except_osv(_('Error'), _('Wrong python condition defined for salary rule %s (%s)') % (
                rule.name, rule.code))


class pedagogy_rule_category(osv.osv):
    _name = 'pedagogy.rule.category'
    _inherit = 'hr.salary.rule.category'

    _columns = {
        'billing_parent_id': fields.many2one('pedagogy.rule.category', 'Parent',
                                             help='Linking a billing category to its parent is used only for the reporting purpose.'),
        'billing_children_ids': fields.one2many('pedagogy.rule.category', 'billing_parent_id', 'Children'),
    }


class pedagogy_billing_structure(osv.osv):
    _name = 'pedagogy.billing.structure'
    _inherit = 'hr.payroll.structure'

    _columns = {
        'billing_parent_id': fields.many2one('pedagogy.billing.structure', 'Parent'),
        'billing_children_ids': fields.one2many('pedagogy.billing.structure', 'parent_id', 'Children'),
        'billing_rule_ids': fields.many2many('pedagogy.rule', 'hr_structure_billing_rule_rel', 'billing_struct_id',
                                             'rule_id', 'Billing Rules'),
    }

    def copy(self, cr, uid, id, default=None, context=None):
        '''
        Create a new record in hr_payroll_structure model from existing one
        @param cr: cursor to database
        @param user: id of current user
        @param id: list of record ids on which copy method executes
        @param default: dict type contains the values to be override during copy of object
        @param context: context arguments, like lang, time zone

        @return: returns a id of newly created record
        '''
        if not default:
            default = {}
        default.update({
            'code': self.browse(cr, uid, id, context=context).code + '(copy)',
            'company_id': self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id
        })
        return super(pedagogy_billing_structure, self).copy(cr, uid, id, default, context=context)

    def get_all_rules(self, cr, uid, structure_ids, context=None):
        '''
        @param structure_ids: list of structure
        @return: returns a list of tuple (id, sequence) of rules that are maybe to apply
        '''

        all_rules = []
        for struct in self.browse(cr, uid, structure_ids, context=context):
            all_rules += self.pool.get('pedagogy.rule')._recursive_search_of_rules(cr, uid, struct.billing_rule_ids,
                                                                                   context=context)
        return all_rules

    def _get_parent_structure(self, cr, uid, struct_ids, context=None):
        if not struct_ids:
            return []
        parent = []
        structs = self.browse(cr, uid, struct_ids, context=context)
        for struct in structs:
            if struct and struct.billing_parent_id and struct.billing_parent_id != False:
                parent.append(struct.billing_parent_id.id)
        if parent:
            parent = self._get_parent_structure(cr, uid, parent, context)
        return parent + struct_ids


class pedagogy_billing_input(osv.osv):
    _name = 'pedagogy.billing.input'
    _inherit = 'hr.payslip.input'

    _columns = {
        'bill_id': fields.many2one('pedagogy.billing', 'Bill', required=True, ondelete='cascade', select=True),
        'enrollment_id': fields.many2one('pedagogy.enrollment', 'Enrollment', required=True,
                                         help='The enrollment for which applied this input'),
        'payslip_id': fields.many2one('hr.payslip', 'Pay Slip', ondelete='cascade', select=True),
        'contract_id': fields.many2one('hr.contract', 'Contract', help='The contract for which applied this input'),
    }
    _order = 'bill_id, sequence'


class pedagogy_rule_input(osv.osv):
    _name = 'pedagogy.rule.input'
    _inherit = 'hr.rule.input'

    _columns = {
        'billing_input_id': fields.many2one('pedagogy.rule', 'Billing Rule Input', required=True),
        'input_id': fields.many2one('hr.salary.rule', 'Salary Rule Input')
    }


class pedagogy_billing_line(osv.osv):
    _name = 'pedagogy.billing.line'
    _inherit = 'pedagogy.rule'
    _description = 'Billing Line'
    _order = 'sequence'

    def _calculate_total(self, cr, uid, ids, name, args, context):
        if not ids: return {}
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = float(line.quantity) * line.amount * line.rate / 100
        return res

    _columns = {
        'bill_id': fields.many2one('pedagogy.billing', 'Bill', required=True, ondelete='cascade'),
        'billing_rule_id': fields.many2one('pedagogy.rule', 'Rule'),
        'student_id': fields.many2one('res.partner', 'Student', domain=[('is_student', '=', True)], readonly=True,
                                      states={'draft': [('readonly', False)]}),
        'rate': fields.float('Rate (%)', digits_compute=dp.get_precision('Payroll Rate')),
        'amount': fields.float('Amount', digits_compute=dp.get_precision('Payroll')),
        'quantity': fields.float('Quantity', digits_compute=dp.get_precision('Payroll')),
        'total': fields.function(_calculate_total, method=True, type='float', string='Total',
                                 digits_compute=dp.get_precision('Bill'), store=True),
    }

    _defaults = {
        'quantity': 1.0,
        'rate': 100.0,
    }


class one2many_mod2(fields.one2many):
    def get(self, cr, obj, ids, name, user=None, offset=0, context=None, values=None):
        if context is None:
            context = {}
        if not values:
            values = {}
        res = {}
        for id in ids:
            res[id] = []
        ids2 = obj.pool.get(self._obj).search(cr, user,
                                              [(self._fields_id, 'in', ids), ('appears_on_payslip', '=', True)],
                                              limit=self._limit)
        for r in obj.pool.get(self._obj)._read_flat(cr, user, ids2, [self._fields_id], context=context,
                                                    load='_classic_write'):
            res[r[self._fields_id]].append(r['id'])
        return res


class pedagogy_billing(osv.osv):
    _name = 'pedagogy.billing'
    _description = 'Pedagogy Billing'
    _order = 'id desc'

    def _get_lines_rule_category(self, cr, uid, ids, field_names, arg=None, context=None):
        result = {}
        if not ids: return result
        for id in ids:
            result.setdefault(id, [])
        cr.execute('''SELECT pl.bill_id, pl.id FROM pedagogy_billing_line AS pl \
                    LEFT JOIN pedagogy_rule_category AS sh on (pl.billing_category_id = sh.id) \
                    WHERE pl.bill_id in %s \
                    GROUP BY pl.bill_id, pl.sequence, pl.id ORDER BY pl.sequence''', (tuple(ids),))
        res = cr.fetchall()
        for r in res:
            result[r[0]].append(r[1])
        return result

    def _amount_all(self, cr, uid, ids, name, args, context=None):
        res = {}
        for bill in self.browse(cr, uid, ids, context=context):
            res[bill.id] = 0.0
            for line in bill.line_ids:
                if line.code == 'NET':
                    res[bill.id] += float(line.quantity) * line.amount * line.rate / 100
        return res

    def on_change_month(self, cr, uid, ids, month, context=None):
        try:
            pedagogy_school_year_obj = self.pool.get('pedagogy.school.year')
            pedagogy_billing_run_obj = self.pool.get('pedagogy.billing.run')
            query = [('date_start', '<=', datetime.now()), ('date_end', '>=', datetime.now())]
            school_year_id = pedagogy_school_year_obj.search(cr, uid, query)
            if school_year_id:
                school_year = pedagogy_school_year_obj.browse(cr, uid, school_year_id)
                periods = pedagogy_billing_run_obj.list_months(cr, uid, school_year[0].date_start,
                                                               school_year[0].date_end)
                for period in periods:
                    if period.split('/')[0] == month:
                        year = period.split('/')[1]
                        date_start = date(int(year), int(month), 1)
                        date_end = date_start + relativedelta(months=1, days=-1)
                        value = {
                            'date_from': date_start.strftime(DATE_FORMAT),
                            'date_to': date_end.strftime(DATE_FORMAT)
                        }
                        return {'value': value}
                raise osv.except_osv('Error', 'O mês escolhido não abrange o ano escolar!')
        except ValueError:
            raise osv.except_osv('Error', 'No school year configured for current date!')

    def _get_class_type_if_exists(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for billing in self.browse(cr, uid, ids):
            class_year = billing.class_year_id
            if class_year and hasattr(class_year, 'class_type'):
                if class_year.class_type.is_curricular:
                    res[billing.id] = _('Curricular')
                else:
                    res[billing.id] = _('Non-Curricular')
        return res

    _columns = {
        'name': fields.char('Description', size=120, required=False, readonly=True,
                            states={'draft': [('readonly', False)]}),
        'number': fields.char('Reference', size=64, required=False, readonly=True,
                              states={'draft': [('readonly', False)]}),
        'month': fields.selection([('01', 'January'), ('02', 'February'), ('03', 'March'), ('04', 'April'),
                                   ('05', 'May'), ('06', 'June'), ('07', 'July'), ('08', 'August'), ('09', 'September'),
                                   ('10', 'October'), ('11', 'November'), ('12', 'December')], 'Month', required=True,
                                  readonly=True, states={'draft': [('readonly', False)]}),
        'date_from': fields.date('Date From', readonly=True, states={'draft': [('readonly', False)]}, required=True),
        'date_to': fields.date('Date To', readonly=True, states={'draft': [('readonly', False)]}, required=True),
        'student_id': fields.many2one('res.partner', 'Student',
                                      domain=[('is_student', '=', True), ('enrollment_id', '!=', False)], required=True,
                                      readonly=True, states={'draft': [('readonly', False)]}),
        'employee_id': fields.many2one('hr.employee', 'Employee', readonly=True,
                                       states={'draft': [('readonly', False)]}),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('confirm', 'Confirmed'),
            ('cancel', 'Canceled'),
        ],
            'State', select=True, readonly=True, help='* When the billing is created the state is \'Draft\'.\
                                        \n* If the billing is under verification, the state is \'Waiting\'. \
                                        \n* If the billing is confirmed then state is set to \'Confirmed\'.\
                                        \n* If the billing is invoiced then state is set to \'Invoiced\'.\
                                        \n* When user cancel the invoice associated the state is \'Canceled\'.\
                                        \n* When user pay the invoice associated to the billin  the state is \'Canceled\'.\
                                        \n* When user cancel billing the state is \'Canceled\'.'),
        'invoicee_id': fields.many2one('res.partner', 'Invoicee', required=True, readonly=True,
                                       states={'draft': [('readonly', False)]}),
        'enrollment_id': fields.many2one('pedagogy.enrollment', 'Enrollment', readonly=True,
                                         states={'draft': [('readonly', False)]},
                                         domain="[('student_id', '=', student_id), ('invoicee_id', '!=', False)]"),
        'class_year_id': fields.related('enrollment_id', 'class_year_id', type='many2one',
                                        relation='pedagogy.class.year', readonly=True, store=True, string='Class Year'),
        'class_year_curricular': fields.function(_get_class_type_if_exists, type='char', method=True, readonly=True,
                                                 store=True, string='Class Type'),
        'line_ids': one2many_mod2('pedagogy.billing.line', 'bill_id', 'Billing Lines', readonly=True,
                                  states={'draft': [('readonly', False)]}),
        'input_line_ids': fields.one2many('pedagogy.billing.input', 'bill_id', 'Billing Inputs', required=False,
                                          readonly=True, states={'draft': [('readonly', False)]}),
        'run_id': fields.many2one('pedagogy.billing.run', 'Billing Batches', readonly=True,
                                  states={'draft': [('readonly', False)]}),
        'struct_id': fields.many2one('pedagogy.billing.structure', 'Structure', readonly=True,
                                     states={'draft': [('readonly', False)]},
                                     help='Defines the rules that have to be applied to this bill, accordingly to the enrollment chosen. If you let empty the field enrollment, this field isn\'t mandatory anymore and thus the rules applied will be all the rules set on the structure of all enrollments of the student valid for the chosen period'),
        'company_id': fields.many2one('res.company', 'Company', required=False, readonly=True,
                                      states={'draft': [('readonly', False)]}),
        'paid': fields.boolean('Made Payment Order ? ', required=False, readonly=True,
                               states={'draft': [('readonly', False)]}),
        'note': fields.text('Description', readonly=True, states={'draft': [('readonly', False)]}),
        'details_by_rule_category': fields.function(_get_lines_rule_category, method=True, type='one2many',
                                                    relation='pedagogy.billing.line',
                                                    string='Details by Billing Rule Category'),
        'credit_note': fields.boolean('Credit Note', help='Indicates this payslip has a refund of another',
                                      readonly=True, states={'draft': [('readonly', False)]}),
        #            'date_due':fields.date('Date Due', size=64, readonly=True, states={'draft': [('readonly', False)]}),
        'payment_term_id': fields.many2one('account.payment.term', 'Payment Terms', readonly=True,
                                           states={'draft': [('readonly', False)]},
                                           help="If you use payment terms, the due date will be computed automatically at the generation " \
                                                "of accounting entries. If you keep the payment term and the due date empty, it means direct payment. " \
                                                "The payment term may compute several due dates, for example 50% now, 50% in one month."),
        'amount_total': fields.function(_amount_all, digits_compute=dp.get_precision('Payroll'), method=True,
                                        string='Total', store=True),
    }

    _defaults = {
        'month': lambda *a: date.today().strftime('%m'),
        #        'date_from': lambda *a: time.strftime('%Y-%m-01'),
        #        'date_to': lambda *a: str(datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1))[:10],
        'state': 'draft',
        'credit_note': False,
        'company_id': lambda self, cr, uid, context: \
            self.pool.get('res.users').browse(cr, uid, uid,
                                              context=context).company_id.id,
    }

    def _check_dates(self, cr, uid, ids, context=None):
        for bill in self.browse(cr, uid, ids, context=context):
            if bill.date_from > bill.date_to:
                return False
        return True

    _constraints = [(_check_dates, 'Bill Date From must be before Date To.', ['date_from', 'date_to'])]

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
            'basic_amount': 0.0
        })
        return super(pedagogy_billing, self).copy(cr, uid, id, default, context=context)

    def cancel_sheet(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'cancel'}, context=context)

    #    def process_sheet(self, cr, uid, ids, context=None):
    #        return self.write(cr, uid, ids, {'state': 'confirm'}, context=context)

    def bill_verify_sheet(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'confirm'}, context=context)

    def refund_sheet(self, cr, uid, ids, context=None):
        mod_obj = self.pool.get('ir.model.data')
        wf_service = netsvc.LocalService('workflow')
        for bill in self.browse(cr, uid, ids, context=context):
            id_copy = self.copy(cr, uid, bill.id, {'credit_note': True, 'name': _('Refund: ') + bill.name},
                                context=context)
            self.pedagogy_compute_sheet(cr, uid, [id_copy], context=context)
            wf_service.trg_validate(uid, 'pedagogy.billing', id_copy, 'bill_verify_sheet', cr)
            wf_service.trg_validate(uid, 'pedagogy.billing', id_copy, 'process_sheet', cr)

        form_id = mod_obj.get_object_reference(cr, uid, 'pedagogy_billing', 'view_billing_form')
        form_res = form_id and form_id[1] or False
        tree_id = mod_obj.get_object_reference(cr, uid, 'pedagogy_billing', 'view_billing_tree')
        tree_res = tree_id and tree_id[1] or False
        return {
            'name': _('Refund Bill'),
            'view_mode': 'tree, form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'pedagogy.billing',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'domain': '[(\'id\', \'in\', %s)]' % [id_copy],
            'views': [(tree_res, 'tree'), (form_res, 'form')],
            'context': {}
        }

    def check_done(self, cr, uid, ids, context=None):
        return True

    def onchange_enrollment_id(self, cr, uid, ids, date_from, date_to, student_id=False, enrollment_id=False,
                               context=None):
        if context is None:
            context = {}
        res = {'value': {
            'line_ids': [],
            'input_ids': [],
            'name': '',
        }
        }
        context.update({'enrollment_id': True})
        if not enrollment_id:
            res['value'].update({'struct_id': False})
            return res
        return self.onchange_student_id(cr, uid, ids, date_from=date_from, date_to=date_to, student_id=student_id,
                                        enrollment_id=enrollment_id, context=context)

    def onchange_student(self, cr, uid, ids, student_id, date_from, context=None):
        partner_obj = self.pool.get('res.partner')
        if context is None:
            context = {}
        res = {'value': {
            'line_ids': [],
            'input_line_ids': [],
            'name': '',
            'enrollment_id': False,
            'struct_id': False,
            'invoicee_id': False,
        }
        }
        if not student_id or not date_from:
            return res
        student_id = partner_obj.browse(cr, uid, student_id, context=context)
        ttyme = datetime.fromtimestamp(time.mktime(time.strptime(date_from, '%Y-%m-%d')))
        enrollment_id = student_id.enrollment_id
        res['value'].update({'invoicee_id': student_id.tutor_id.id,
                             'name': _('Payment Notice: %s') % (tools.ustr(ttyme.strftime('%B-%Y'))),
                             'enrollment_id': enrollment_id.id,
                             'company_id': student_id.company_id.id})
        return res

    def onchange_struct_id(self, cr, uid, ids, date_from, date_to, student_id=False, enrollment_id=False,
                           struct_id=False, context=None):
        if context is None:
            context = {}
        input_obj = self.pool.get('pedagogy.billing.input')
        # delete old input lines
        old_input_ids = ids and input_obj.search(cr, uid, [('bill_id', '=', ids[0])], context=context) or False
        if old_input_ids:
            input_obj.unlink(cr, uid, old_input_ids, context=context)

        # defaults
        res = {'value': {
            'line_ids': [],
            'input_line_ids': [],
            'struct_id': False,
        }
        }
        if (not student_id) or (not date_from) or (not date_to) or (not struct_id):
            return res

        # computation of the billing input
        input_line_ids = self.get_inputs_by_struct(cr, uid, [struct_id], enrollment_id, date_from, date_to,
                                                   context=context)
        res['value'].update({'input_line_ids': input_line_ids, 'struct_id': struct_id})
        return res

    def onchange_student_id(self, cr, uid, ids, date_from, date_to, student_id=False, enrollment_id=False,
                            context=None):
        partner_obj = self.pool.get('res.partner')
        input_obj = self.pool.get('pedagogy.billing.input')
        enrollment_obj = self.pool.get('pedagogy.enrollment')
        module_obj = self.pool.get('ir.module.module')
        if context is None:
            context = {}
        # delete old input lines
        old_input_ids = ids and input_obj.search(cr, uid, [('bill_id', '=', ids[0])], context=context) or False
        if old_input_ids:
            input_obj.unlink(cr, uid, old_input_ids, context=context)

        # defaults
        res = {'value': {
            'line_ids': [],
            'input_line_ids': [],
            'name': '',
            'enrollment_id': False,
            'struct_id': False,
            'payment_term_id': False,
            'invoicee_id': False,
        }
        }
        if (not student_id) or (not date_from) or (not date_to):
            return res
        ttyme = datetime.fromtimestamp(time.mktime(time.strptime(date_from, '%Y-%m-%d')))
        student_id = partner_obj.browse(cr, uid, student_id, context=context)
        res['value'].update({
            'name': _('Payment Notice: %s') % (tools.ustr(ttyme.strftime('%B-%Y'))),
            'company_id': student_id.company_id.id
        })

        enrollment_ids = []
        if not context.get('enrollment_id', False):
            # fill with the enrollment of class curricular of the student
            if module_obj.search(cr, uid, [('name', '=', 'pedagogy_extra_activities'), ('state', '=', 'installed')]):
                enrollment_ids = enrollment_obj.search(cr, uid, [('student_id', '=', student_id.id),
                                                                 ('invoicee_id', '!=', False),
                                                                 ('state', '=', 'enrolled'), (
                                                                 'class_year_id.class_type_id.is_curricular', '=',
                                                                 True)])
            if not enrollment_ids:
                enrollment_ids = self.get_student_enrollment(cr, uid, student_id, False, False, date_from, date_to,
                                                             context=context)
            enrollment = enrollment_obj.browse(cr, uid, enrollment_ids)
            res['value'].update({
                'struct_id': enrollment and enrollment[0].struct_id.id or False,
                'payment_term_id': enrollment and enrollment[0].student_id.property_payment_term.id or enrollment[
                    0].class_year_id.class_id.group_id.payment_term_id.id or False,
                'enrollment_id': enrollment and enrollment[0].id or False,
                'invoicee_id': enrollment and enrollment[0].invoicee_id.id or False,
                'class_year_id': enrollment and enrollment[0].id and enrollment[0].class_year_id.id or False,
            })
        else:
            if enrollment_id:
                # set the list of contract for which the input have to be filled
                enrollment_ids = [enrollment_id]
                # fill the structure with the one on the selected contract
                enrollment_record = enrollment_obj.browse(cr, uid, enrollment_id, context=context)
                res['value'].update({
                    'struct_id': enrollment_record.struct_id.id,
                    'payment_term_id': enrollment_record.student_id.property_payment_term.id or enrollment_record.class_year_id.class_id.group_id.payment_term_id.id,
                    'enrollment_id': enrollment_id,
                    'invoicee_id': enrollment_record.invoicee_id.id,
                    'class_year_id': enrollment_record.class_year_id.id or False,
                })
            else:
                # if we don't give the contract, then the input to fill should be for all current enrollments of the student
                enrollment_ids = self.get_student_enrollment(cr, uid, student_id, False, False, date_from, date_to,
                                                             context=context)

        if not enrollment_ids:
            return res

        # computation of the billing input
        input_line_ids = self.get_inputs(cr, uid, enrollment_ids, date_from, date_to, context=context)
        res['value'].update({
            'input_line_ids': input_line_ids,
        })
        return res

    def get_student_enrollment(self, cr, uid, student, invoicee, p_class, date_from, date_to, context=None):
        '''
        @param student: browse record of student
        @param date_from: date field
        @param date_to: date field
        @return: returns the ids of all the enrollments for the given student that need to be considered for the given dates
        '''
        enroll_obj = self.pool.get('pedagogy.enrollment')
        clause = []
        # a enrollment is valid if it ends between the given dates
        clause_1 = ['&', ('class_year_id.year_id.date_start', '<=', date_to),
                    ('class_year_id.year_id.date_end', '>=', date_from)]
        # OR if it starts between the given dates
        clause_2 = ['&', ('class_year_id.year_id.date_start', '<=', date_to),
                    ('class_year_id.year_id.date_end', '>=', date_from)]
        # OR if it starts before the date_from and finish after the date_end (or never finish)
        clause_3 = [('class_year_id.year_id.date_start', '<=', date_from), '|',
                    ('class_year_id.year_id.date_end', '=', False), ('class_year_id.year_id.date_end', '>=', date_to)]
        clause_final = [('state', '=', 'enrolled'), ('student_id', '=', student.id), ('invoicee_id', '!=', False), '|',
                        '|'] + clause_1 + clause_2 + clause_3
        if invoicee:
            clause_final = clause_final + [('invoicee_id', '=', invoicee.id)]
        if p_class:
            clause_final = clause_final + [('class_year_id', '=', p_class.id)]
        enrollment_ids = enroll_obj.search(cr, uid, clause_final, context=context)
        return enrollment_ids

    def get_inputs(self, cr, uid, enrollment_ids, date_from, date_to, context=None):
        res = []
        enroll_obj = self.pool.get('pedagogy.enrollment')
        rule_obj = self.pool.get('pedagogy.rule')

        structure_ids = enroll_obj.get_all_structures_old(cr, uid, enrollment_ids, context=context)
        rule_ids = self.pool.get('pedagogy.billing.structure').get_all_rules(cr, uid, structure_ids, context=context)
        sorted_rule_ids = [id for id, sequence in sorted(rule_ids, key=lambda x: x[1])]

        for enroll in enroll_obj.browse(cr, uid, enrollment_ids, context=context):
            for rule in rule_obj.browse(cr, uid, sorted_rule_ids, context=context):
                if rule.billing_input_ids:
                    for input in rule.billing_input_ids:
                        inputs = {
                            'name': input.name,
                            'code': input.code,
                            'enrollment_id': enroll.id,
                        }
                        res += [inputs]
        return res

    def get_inputs_by_struct(self, cr, uid, struct, enrollment, date_from, date_to, context=None):
        res = []
        enroll_obj = self.pool.get('pedagogy.enrollment')
        rule_obj = self.pool.get('pedagogy.rule')
        structure_ids = list(
            set(self.pool.get('pedagogy.billing.structure')._get_parent_structure(cr, uid, struct, context=context)))
        rule_ids = self.pool.get('pedagogy.billing.structure').get_all_rules(cr, uid, structure_ids, context=context)
        sorted_rule_ids = [id for id, sequence in sorted(rule_ids, key=lambda x: x[1])]

        for rule in rule_obj.browse(cr, uid, sorted_rule_ids, context=context):
            if rule.billing_input_ids:
                for input in rule.billing_input_ids:
                    inputs = {
                        'name': input.name,
                        'code': input.code,
                        'enrollment_id': enrollment,
                    }
                    res += [inputs]
        return res

    def pedagogy_compute_sheet(self, cr, uid, ids, context=None):
        bill_line_pool = self.pool.get('pedagogy.billing.line')
        sequence_obj = self.pool.get('ir.sequence')
        enroll_pool = self.pool.get('pedagogy.enrollment')
        if context is None:
            context = {}
        for bill in self.browse(cr, uid, ids, context=context):
            number = sequence_obj.get(cr, uid, 'billing')
            # delete old billing lines
            old_billing_ids = bill_line_pool.search(cr, uid, [('bill_id', '=', bill.id)], context=context)
            #            old_billing_ids
            if old_billing_ids:
                bill_line_pool.unlink(cr, uid, old_billing_ids, context=context)
            if bill.enrollment_id:
                # set the list of enrollment for which the rules have to be applied
                enrollment_ids = [bill.enrollment_id.id]
            else:
                if bill.invoicee_id:
                    # if we don't give the enrollment, then the rules to apply should be for all current enrollments with the same invoicee of the student
                    enrollment_ids = self.get_student_enrollment(cr, uid, bill.student_id, bill.invoicee_id, False,
                                                                 bill.date_from, bill.date_to, context)
                else:
                    # if we don't give the enrollment, then the rules to apply should be for all current enrollments of the student
                    enrollment_ids = self.get_student_enrollment(cr, uid, bill.student_id, False, False, bill.date_from,
                                                                 bill.date_to, context=context)
            lines = [(0, 0, line) for line in
                     self.pool.get('pedagogy.billing').get_billing_lines(cr, uid, enrollment_ids, bill.id,
                                                                         context=context)]
            self.write(cr, uid, [bill.id], {'line_ids': lines, 'number': number,}, context=context)
        return True

    def get_extra_rules(self, cr, uid, enrollment_ids, bill_id, context):
        '''This method exists only for being extended, to allow subclasses to
        'inject' billing rules into the process'''
        return []

    def get_protocol(self, cr, uid, code):
        return 0.0

    def get_all_structures(self, cr, uid, bill_ids, context=None):
        '''
        @param enrollment_ids: list of enrollments
        @return: the structures linked to the given enrollments, ordered by hierachy (parent=False first, then first level children and so on) and without duplicata
        '''
        all_structures = []
        structure_ids = [bill.struct_id.id for bill in self.browse(cr, uid, bill_ids, context=context)]
        return list(set(
            self.pool.get('pedagogy.billing.structure')._get_parent_structure(cr, uid, structure_ids, context=context)))

    def get_billing_lines(self, cr, uid, enrollment_ids, bill_id, context):
        def _sum_billing_rule_category(localdict, category, amount):
            if category.parent_id:
                localdict = _sum_billing_rule_category(localdict, category.billing_parent_id, amount)
            localdict['categories'].dict[category.code] = category.code in localdict['categories'].dict and \
                                                          localdict['categories'].dict[category.code] + amount or amount
            return localdict

        class BrowsableObject(object):
            def __init__(self, pool, cr, uid, student_id, dict):
                self.pool = pool
                self.cr = cr
                self.uid = uid
                self.student_id = student_id
                self.dict = dict

            def __getattr__(self, attr):
                return attr in self.dict and self.dict.__getitem__(attr) or 0.0

        class InputLine(BrowsableObject):
            '''a class that will be used into the python code, mainly for usability purposes'''

            def sum(self, code, from_date, to_date=None):
                if to_date is None:
                    to_date = datetime.now().strftime('%Y-%m-%d')
                result = 0.0
                self.cr.execute('SELECT sum(amount) as sum\
                            FROM pedagogy_billing as hp, pedagogy_billing_input as pi \
                            WHERE hp.student_id = %s AND hp.state = \'done\' \
                            AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pi.billing_id AND pi.code = %s',
                                (self.student_id, from_date, to_date, code))
                res = self.cr.fetchone()[0]
                return res or 0.0

        class Billing(BrowsableObject):
            '''a class that will be used into the python code, mainly for usability purposes'''

            def sum(self, code, from_date, to_date=None):
                if to_date is None:
                    to_date = datetime.now().strftime('%Y-%m-%d')
                self.cr.execute('SELECT sum(case when hp.credit_note = False then (pl.total) else (-pl.total) end)\
                            FROM pedagogy_billing as hp, hr_payslip_line as pl \
                            WHERE hp.student_id = %s AND hp.state = \'done\' \
                            AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pl.slip_id AND pl.code = %s',
                                (self.student_id, from_date, to_date, code))
                res = self.cr.fetchone()
                return res and res[0] or 0.0

            def acert(self, code):
                return self.pool.get('pedagogy.billing').get_adjustment(self.cr, self.uid, code, self.student_id)

            def sum_younger_brothers(self):
                res_partner_obj = self.pool.get('res.partner')
                student = res_partner_obj.browse(cr, uid, [self.student_id])[0]
                brothers_father = []
                brothers_mother = []
                if student.father:
                    brothers_father = res_partner_obj.search(cr, uid, [('father_id', '=', student.father_id.id),
                                                                       ('birth_date', '>', student.birth_date),
                                                                       ('id', '!=', student.id)])
                if student.mother_id:
                    brothers_mother = res_partner_obj.search(cr, uid, [('mother_id', '=', student.mother_id.id),
                                                                       ('birth_date', '>', student.birth_date),
                                                                       ('id', '!=', student.id)])
                brothers = set(brothers_father + brothers_mother)
                return len(brothers)

            def sum_older_brothers(self):
                res_partner_obj = self.pool.get('res.partner')
                student = res_partner_obj.browse(cr, uid, [self.student_id])[0]
                brothers_father = []
                brothers_mother = []
                if student.father_id:
                    brothers_father = res_partner_obj.search(cr, uid, [('father_id', '=', student.father_id.id),
                                                                       ('birth_date', '<', student.birth_date),
                                                                       ('id', '!=', student.id)])
                if student.mother_id:
                    brothers_mother = res_partner_obj.search(cr, uid, [('mother_id', '=', student.mother_id.id),
                                                                       ('birth_date', '<', student.birth_date),
                                                                       ('id', '!=', student.id)])
                brothers = set(brothers_father + brothers_mother)
                return len(brothers)

        # we keep a dict with the result because a value can be overwritten by another rule with the same code
        result_dict = {}
        rules = {}
        categories_dict = {}
        blacklist = []
        billing_obj = self.pool.get('pedagogy.billing')
        inputs_obj = self.pool.get('hr.payslip.worked_days')
        obj_rule = self.pool.get('hr.salary.rule')
        obj_bill_rule = self.pool.get('pedagogy.rule')
        enroll_pool = self.pool.get('pedagogy.enrollment')
        structure_pool = self.pool.get('pedagogy.billing.structure')
        bill = billing_obj.browse(cr, uid, bill_id, context=context)
        inputs = {}
        for input_line in bill.input_line_ids:
            inputs[input_line.code] = input_line

        categories_obj = BrowsableObject(self.pool, cr, uid, bill.student_id.id, categories_dict)
        input_obj = InputLine(self.pool, cr, uid, bill.student_id.id, inputs)
        bill_obj = Billing(self.pool, cr, uid, bill.student_id.id, bill)
        rules_obj = BrowsableObject(self.pool, cr, uid, bill.student_id.id, rules)
        # for get protocols of student
        # protocol_obj = Protocol(self.pool, cr, uid, bill.student_id.id, bill.student_id.protocol_ids)
        localdict = {'categories': categories_obj, 'rules': rules_obj, 'bill': bill_obj, 'inputs': input_obj}

        for enroll in self.pool.get('pedagogy.enrollment').browse(cr, uid, enrollment_ids, context=context):
            student = enroll.student_id
            # get the ids of the structures on the enrolls and their parent id as well
            structure_ids_old = enroll_pool.get_all_structures_old(cr, uid, [enroll.id], context=context)
            structure_ids = billing_obj.get_all_structures(cr, uid, [bill.id], context=context)
            # get the rules of the structure and thier children
            rule_ids = structure_pool.get_all_rules(cr, uid, structure_ids, context=context)
            rules_ad_hoc = self.get_extra_rules(cr, uid, enrollment_ids, bill_id, context=context)
            rule_ids += self.pool.get('pedagogy.rule')._recursive_search_of_rules(cr, uid, rules_ad_hoc,
                                                                                  context=context)
            # run the rules by sequence
            sorted_rule_ids = [id for id, sequence in sorted(rule_ids, key=lambda x: x[1])]
            localdict.update({'enrollment_id': enroll, 'student_id': student})
            all_rules = obj_bill_rule.browse(cr, uid, sorted_rule_ids, context=context)
            # all_rules += self.get_extra_rules(cr, uid, enrollment_ids, bill_id, context=context)
            for rule in all_rules:
                key = rule.code + '-' + str(enroll.id)
                localdict['result'] = None
                localdict['result_qty'] = 1.0
                # check if the rule can be applied
                if obj_bill_rule.billing_satisfy_condition(cr, uid, rule.id, localdict,
                                                           context=context) and rule.id not in blacklist:
                    # compute the amount of the rule
                    amount, qty, rate = obj_bill_rule.billing_compute_rule(cr, uid, rule.id, localdict, context=context)
                    # check if there is already a rule computed with that code
                    previous_amount = rule.code in localdict and localdict[rule.code] or 0.0
                    # set/overwrite the amount computed for this rule in the localdict
                    tot_rule = amount * qty * rate / 100.0
                    localdict[rule.code] = tot_rule
                    rules[rule.code] = rule
                    # sum the amount for its salary category
                    localdict = _sum_billing_rule_category(localdict, rule.billing_category_id,
                                                           tot_rule - previous_amount)
                    # create/overwrite the rule in the temporary results
                    result_dict[key] = {
                        'billing_rule_id': rule.id,
                        'enrollment_id': enroll.id,
                        # 'product_id': rule.product_id.id or False,
                        'name': rule.name,
                        'code': rule.code,
                        'billing_category_id': rule.billing_category_id.id,
                        'sequence': rule.sequence,
                        'appears_on_payslip': rule.appears_on_payslip,
                        'condition_select': rule.condition_select,
                        'condition_python': rule.condition_python,
                        'condition_range': rule.condition_range,
                        'condition_range_min': rule.condition_range_min,
                        'condition_range_max': rule.condition_range_max,
                        'amount_select': rule.amount_select,
                        'amount_fix': rule.amount_fix,
                        'amount_python_compute': rule.amount_python_compute,
                        'amount_percentage': rule.amount_percentage,
                        'amount_percentage_base': rule.amount_percentage_base,
                        'register_id': rule.register_id.id,
                        'amount': amount,
                        'student_id': enroll.student_id.id,
                        'quantity': qty,
                        'rate': rate,
                    }
                else:
                    # blacklist this rule and its children
                    blacklist += [id for id, seq in
                                  self.pool.get('pedagogy.rule')._recursive_search_of_rules(cr, uid, [rule],
                                                                                            context=context)]

        result = [value for code, value in result_dict.items()]
        return result

    def _get_invoicees(self, cr, uid, ids, student_id, date_from, date_to, context):
        enroll_obj = self.pool.get('pedagogy.enrollment')
        if context is None:
            context = {}
        res = []
        if (not student_id) or (not date_from) or (not date_to):
            return res
        enroll_ids = self.get_student_enrollment(cr, uid, student_id, False, False, date_from, date_to, context)
        invoicees = list(set([line.invoicee_id for line in enroll_obj.browse(cr, uid, enroll_ids) if line.invoicee_id]))
        if invoicees:
            res = invoicees
        return res


class pedagogy_billing_run(osv.osv):
    _name = 'pedagogy.billing.run'
    _inherit = 'hr.payslip.run'
    _order = 'id desc'

    translated_months = {'01': 'Janeiro',
                         '02': 'Fevereiro',
                         '03': 'Março',
                         '04': 'Abril',
                         '05': 'Maio',
                         '06': 'Junho',
                         '07': 'Julho',
                         '08': 'Agosto',
                         '09': 'Setembro',
                         '10': 'Outubro',
                         '11': 'Novembro',
                         '12': 'Dezembro'}

    def list_months(self, cr, uid, start_date, end_date):
        ds = datetime.strptime(start_date, '%Y-%m-%d')
        periods = []
        while ds.strftime('%Y-%m-%d') < end_date:
            de = ds + relativedelta(months=1, days=-1)

            if de.strftime('%Y-%m-%d') > end_date:
                de = datetime.strptime(end_date, '%Y-%m-%d')
            periods.append(ds.strftime('%m/%Y'))
            ds = ds + relativedelta(months=1)
        return periods

    def on_change_month(self, cr, uid, ids, month, context=None):
        v = {}
        d = {}

        pedagogy_school_year_obj = self.pool.get('pedagogy.school.year')
        school_year_id = pedagogy_school_year_obj.search(cr, uid, [('date_start', '<=', datetime.now()),
                                                                   ('date_end', '>=', datetime.now())])
        school_year = pedagogy_school_year_obj.browse(cr, uid, school_year_id)
        if school_year:
            periods = self.list_months(cr, uid, school_year[0].date_start, school_year[0].date_end)
            for period in periods:
                if period.split('/')[0] == month:
                    year = period.split('/')[1]
                    date_start = date(int(year), int(month), 1)
                    date_end = date_start + relativedelta(months=1, days=-1)
                    v['name'] = ('%s - %s' % (self.translated_months[month], year))
                    v['date_start'] = str(date_start)
                    v['date_end'] = str(date_end)
                    return {'value': v, 'domain': d}
            raise osv.except_osv('Error', 'O mês escolhido não abrange o ano escolar!')
        return {}

    def draft_payslip_run(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService('workflow')
        pedagogy_bill_obj = self.pool.get('pedagogy.billing')
        for bill in ids:
            bill_ids = pedagogy_bill_obj.search(cr, uid, [('run_id', '=', bill)])
            data_bill = pedagogy_bill_obj.read(cr, uid, bill_ids, ['state'], context=context)
            for record in data_bill:
                if record['state'] not in ('confirm'):
                    raise osv.except_osv(_('Warning'), _(
                        'Selected Bill(s) cannot be turn to draft as they are not in confirmed state!'))
                wf_service.trg_validate(uid, 'pedagogy.billing', record['id'], 'draft_sheet', cr)
        super(pedagogy_billing_run, self).draft_payslip_run(cr, uid, ids, context)
        return True

    def close_payslip_run(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService('workflow')
        pedagogy_bill_obj = self.pool.get('pedagogy.billing')
        for bill in ids:
            bill_ids = pedagogy_bill_obj.search(cr, uid, [('run_id', '=', bill)])
            data_bill = pedagogy_bill_obj.read(cr, uid, bill_ids, ['state'], context=context)
            for record in data_bill:
                if record['state'] not in ('draft'):
                    raise osv.except_osv(_('Warning'),
                                         _('Selected Bill(s) cannot be confirmed as they are not in Draft state!'))
                wf_service.trg_validate(uid, 'pedagogy.billing', record['id'], 'bill_verify_sheet', cr)
        super(pedagogy_billing_run, self).close_payslip_run(cr, uid, ids, context)
        return True

    _columns = {
        'month': fields.selection([('01', 'January'), ('02', 'February'), ('03', 'March'), ('04', 'April'),
                                   ('05', 'May'), ('06', 'June'), ('07', 'July'), ('08', 'August'), ('09', 'September'),
                                   ('10', 'October'), ('11', 'November'), ('12', 'December')], 'Month', required=True,
                                  states={'draft': [('readonly', False)]}),
        'bill_ids': fields.one2many('pedagogy.billing', 'run_id', 'Bills', required=False, readonly=True,
                                    states={'draft': [('readonly', False)]}),
    }
