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

from datetime import date
from datetime import datetime
from dateutil.relativedelta import relativedelta

import decimal_precision as dp
from osv import osv, fields
from tools.translate import _

DATE_FORMAT = '%Y-%m-%d'

SCHEDULE_PAYS = [
    ('1_month', _('Each month')),
    ('2_month', _('Each 2 months')),
    ('3_month', _('Each 3 months')),
    ('4_month', _('Each 4 months')),
    ('5_month', _('Each 5 months')),
    ('6_month', _('Each 6 months')),
    ('annually', _('Annually')),
]


class pedagogy_enrollment(osv.osv):
    _inherit = 'pedagogy.enrollment'

    def onchange_class_year(self, cr, uid, ids, class_year_id, context=None):
        v = {}
        if class_year_id:
            class_year_obj = self.pool.get('pedagogy.class.year')
            class_year = class_year_obj.browse(cr, uid, class_year_id)
            if class_year:
                v['contract_date_start'] = class_year.class_id.group_id.date_from
                v['contract_date_end'] = class_year.class_id.group_id.date_to
                v['struct_id'] = class_year.class_id.group_id.struct_id.id
                v['fee'] = class_year.class_id.group_id.fee
                v['schedule_pay'] = class_year.class_id.group_id.schedule_pay
        return {'value': v}

    def _get_payments(self, cr, uid, enroll):
        pool = self.pool.get('pedagogy.billing.line')
        query = [('bill_id.enrollment_id', '=', enroll.id),
                 ('bill_id.state', '=', 'confirm'),
                 ('billing_category_id.code', '=', 'BASE')]
        return pool.browse(cr, uid, pool.search(cr, uid, query))

    def _amount_residual(self, cr, uid, ids, name, args, context=None):
        res = {}
        for enroll in self.browse(cr, uid, ids):
            payments = self._get_payments(cr, uid, enroll)
            total_paid = sum(payment.total for payment in payments)
            res[enroll.id] = enroll.fee - total_paid
        return res

    def _contract_months(self, enroll):
        if not (enroll.contract_date_start and enroll.contract_date_end):
            return 0
        start = datetime.strptime(enroll.contract_date_start, DATE_FORMAT).date().replace(day=1)
        end = datetime.strptime(enroll.contract_date_end, DATE_FORMAT).date().replace(day=1)
        delta = relativedelta(end, start)
        return delta.years * 12 + delta.months

    def _numberofpayments(self, enroll):
        periodicity = int(enroll.schedule_pay.split('_')[0])
        months = self._contract_months(enroll)
        return ((months / periodicity) + 1) if months > 0 else 1

    def _getnumberofpayments(self, cr, uid, ids, name, args, context=None):
        return dict((e.id, self._numberofpayments(e)) for e in self.browse(cr, uid, ids))

    def _get_monthlyfee(self, cr, uid, ids, name, args, context=None):
        if context is None:
            context = {}
        res = {}
        for enroll in self.browse(cr, uid, ids):
            if enroll.schedule_pay and enroll.fee:
                if enroll.schedule_pay == 'annually':
                    res[enroll.id] = enroll.fee
                else:
                    period = float(enroll.schedule_pay[:1])
                    duration = self._contract_months(enroll)
                    res[enroll.id] = enroll.fee / self._numberofpayments(enroll)
            else:
                res[enroll.id] = 0.00
        return res

    _columns = {
        # 'contract_id': fields.many2one('hr.contract', 'Contract', domain='[('student_id','=',student),('enrollment_id','=',False)]'),
        'contract_date_start': fields.date('Start Date'),
        'contract_date_end': fields.date('End Date'),
        'contract_notes': fields.text('Notes'),
        'fee': fields.float('Fee', digits=(16, 2), help='Anual Fee of the Group Area'),
        'struct_id': fields.many2one('pedagogy.billing.structure', 'Fee Structure'),
        'invoicee_id': fields.many2one('res.partner', 'Invoicee'),
        'schedule_pay': fields.selection(selection=SCHEDULE_PAYS, string='Scheduled Pay', select=True, translate=True),
        'notes': fields.text('Notes'),
        # 'class_duration': fields.related('class_year_id', 'class_id', type='integer', string='Class Duration'),
        'number_of_payments': fields.function(_getnumberofpayments, method=True, type='integer',
                                              string='Number of Payments', readonly=True, help='Number of Payments'),
        'monthly_fee': fields.function(_get_monthlyfee, method=True, type='float', string='Monthly Fee', digits=(16, 2),
                                       help='Monthly Fee of the Class Year'),
        'residual': fields.function(_amount_residual, method=True, digits_compute=dp.get_precision('Account'),
                                    string='Residual'),
        # 'company_id': fields.related('fiscalyear_id', 'company_id', type='many2one', relation='res.company', string='Company', store=True, readonly=True)
        'process': fields.boolean('Continue Process?', help='If true continue processing billing for this enrollment.'),
    }

    _defaults = {
        'schedule_pay': '1_month',
    }

    def get_all_structures_old(self, cr, uid, enrollment_ids, context=None):
        '''
        @param enrollment_ids: list of enrollments
        @return: the structures linked to the given enrollments, ordered by hierachy (parent=False first, then first level children and so on) and without duplicata
        '''
        all_structures = []
        structure_ids = [enroll.struct_id.id for enroll in self.browse(cr, uid, enrollment_ids, context=context)]
        return list(set(
            self.pool.get('pedagogy.billing.structure')._get_parent_structure(cr, uid, structure_ids, context=context)))

    def date_start_change(self, cr, uid, ids, student_id=False, date_start=False, class_year_id=False, context=None):
        #        if student_id and class_year_id:
        #            class_year_obj = self.pool.get('pedagogy.class.year')
        #            class_year_id = class_year_obj.browse(cr, uid, class_year_id)
        #            year_date_start = class_year_id.year_id.date_start
        #            year_date_end = class_year_id.year_id.date_end
        #            if date_start < year_date_start or date_start > year_date_end:
        #                raise osv.except_osv(_('Invalid Date!'), _('Date must be inserted in range of the school year.'))
        return {}

    def date_end_change(self, cr, uid, ids, student_id=False, date_end=False, class_year_id=False, context=None):
        #        if student_id and class_year_id:
        #            class_year_obj = self.pool.get('pedagogy.class.year')
        #            class_year_id = class_year_obj.browse(cr, uid, class_year_id)
        #            year_date_start = class_year_id.year_id.date_start
        #            year_date_end = class_year_id.year_id.date_end
        #            if date_end < year_date_start or date_end > year_date_end:
        #                raise osv.except_osv(_('Invalid Date!'), _('Date must be inserted in range of the school year.'))
        return {}

    def create(self, cr, uid, vals, context=None):
        new_id = super(pedagogy_enrollment, self).create(cr, uid, vals, context)
        if new_id:
            change_line = self.write_change(cr, uid, vals, self.browse(cr, uid, new_id))
            self.write_history_billing(cr, uid, new_id, change_line)
        #             enroll = self.browse(cr, uid, new_id)
        #             classe = getattr(enroll.class_year_id, 'class_id')
        #             if classe.group_id.date_from:
        #                 date_today = date.today().strftime('%Y-%m-%d')
        #                 # if student is inscripted after the classes begin, date_to = current date
        #                 if date_today > enroll.class_year_id.date_start:
        #                     contract_date = date_today
        #                 # else date_from = date_from in group
        #                 else:
        #                     contract_date = classe.group_id.date_start
        #                 self.write(cr, uid, [new_id], {'struct_id': classe.group_id.struct_id.id,
        #                                                'invoicee_id': enroll.student_id.tutor.id,
        #                                                'contract_date_start': contract_date,
        #                                                'contract_date_end': classe.group_id.date_to,
        #                                                'fee': classe.group_id.fee})
        return new_id

    def write(self, cr, uid, ids, vals, context=None):
        # dict: {'date_end': '2012-10-01'}  dict: {'wage': 25, 'schedule_pay': 'semi-annually', 'date_start': '2012-10-04', 'struct_id': 4
        res = super(pedagogy_enrollment, self).write(cr, uid, ids, vals, context=context)
        enrollment_history_obj = self.pool.get('pedagogy.enrollment.history')
        if type(ids).__name__ == 'list':
            for enroll in self.browse(cr, uid, ids):
                if enroll.state == 'canceled' and not (context and 'ending' in context):
                    self.end_contract(cr, uid, [enroll.id], ())
                if enroll.state == 'new' and not (context and 'ending' in context):
                    self.write(cr, uid, [enroll.id], {}, context={'ending': False})
                change_line = self.write_change(cr, uid, vals, enroll)
                self.write_history_billing(cr, uid, enroll.id, change_line)
        return res

    def write_change(self, cr, uid, vals, enroll):
        change_line = []
        for val in vals:
            line = ''
            if val == 'invoicee_id':
                line = unicode(_('Invoicee to: ')) + unicode(enroll.invoicee_id.name)
                change_line.append(unicode(_('In contract changed ')) + line)
            if val == 'struct_id':
                line = unicode(_('Fee Estructure to: ')) + unicode(enroll.struct_id.name)
                change_line.append(unicode(_('In contract changed ')) + line)
            if val == 'schedule_pay':
                line = unicode(_('Schedule Pay to: ')) + unicode(enroll.schedule_pay)
                change_line.append(unicode(_('In contract changed ')) + line)
            if val == 'fee':
                line = unicode(_('Fee to: ')) + unicode(vals[val])
                change_line.append(unicode(_('In contract changed ')) + line)
            if val == 'contract_date_end' and val == 'contract_date_end' != False:
                line = unicode(_('Date End to: ')) + unicode(enroll.contract_date_end)
                #                self.date_end_change(cr, uid, [],  enroll.student_id.id, enroll.contract_date_end, enroll.class_year_id.id, None)
                change_line.append(unicode(_('In contract changed ')) + line)
            if val == 'contract_date_start':
                line = unicode(_('Date Start to: ')) + unicode(enroll.contract_date_start)
                #                self.date_start_change(cr, uid, [], enroll.student_id.id, enroll.contract_date_start, enroll.class_year_id.id,None)
                change_line.append(unicode(_('In contract changed ')) + line)

        return change_line

    def write_history_billing(self, cr, uid, enrollment_id, changes):
        history_obj = self.pool.get('pedagogy.enrollment.history')
        for change in changes:
            history_obj.create(cr, uid, {'enrollment_id': enrollment_id,
                                         'user_id': uid,
                                         'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                         'change': change})
        return True

    def end_contract(self, cr, uid, ids, *args):
        '''
            Map end date in contract when enrollment is canceled
        '''
        for enrollment in self.browse(cr, uid, ids):
            if enrollment.invoicee_id:
                self.write(cr, uid, [enrollment.id], {'contract_date_end': date.today().strftime('%Y-%m-%d')},
                           context={'ending': True})
        return True
