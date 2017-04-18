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

from datetime import datetime
from dateutil import relativedelta

from osv import fields, osv
from tools.translate import _

DATE_FORMAT = '%Y-%m-%d'


class pedagogy_billing_students(osv.osv_memory):
    _name = 'pedagogy.billing.students'
    _description = 'Generate billing for all selected students'

    def _get_students_enrolled(self, cr, uid, context):
        res = []
        id = context.get('active_id', False)
        if id:
            enroll_obj = self.pool.get('pedagogy.enrollment')
            enrollments = enroll_obj.search(cr, uid, [('state', '=', 'enrolled'), ('invoicee_id', '!=', False),
                                                      ('struct_id', '!=', False)])
            student_enrolled = list(set([line.student_id.id for line in enroll_obj.browse(cr, uid, enrollments)]))
            res = student_enrolled
        return res

    _columns = {
        'student_ids': fields.many2many('res.partner', string='Students', required=True),
    }

    _defaults = {
        'student_ids': _get_students_enrolled,
    }

    def _get_periodicity(self, enroll):
        if enroll.schedule_pay == 'annualy':
            period = 12
        else:
            period = int(enroll.schedule_pay.split('_')[0])
        return period

    def _generate_reverse_billing_period(self, enroll, until_date):
        periodicity = self._get_periodicity(enroll)
        delta = relativedelta.relativedelta(months=-(periodicity - 1))
        return until_date + delta

    def _get_payments_for_period(self, cr, uid, enroll, from_date, to_date):
        convert = lambda dt: dt.strftime(DATE_FORMAT)
        bill_pool = self.pool.get('pedagogy.billing')
        query = [('student_id', '=', enroll.student_id.id),
                 ('state', '=', 'confirm'),
                 ('enrollment_id', '=', enroll.id),
                 ('line_ids.billing_category_id.code', '=', 'BASE'),
                 ('date_from', '>=', convert(from_date)),
                 ('date_to', '<=', to_date)]
        return len(bill_pool.search(cr, uid, query)) > 0

    #    def _verify_past_dates(self, cr, uid, enroll, past_dates):
    #        if len(past_dates) < 1:
    #            return
    #        bill_pool = self.pool.get('pedagogy.billing')
    #        def create_query(dates):
    #            q = lambda d: ('month','=',d.strftime('%m'))
    #            if len(dates) == 1:
    #                return [q(dates[0])]
    #            else:
    #                current, rest = dates[0], dates[1:]
    #                return ['|',q(current)] + create_query(rest)
    #        query = [('state', '=', 'confirmed')] + create_query(past_dates)
    #        if len(bill_pool.search(cr, uid, query)) < len(past_dates):
    #            diff = len(past_dates) - len(bill_pool.search(cr, uid, query))
    #            sn = enroll.student.name
    #            raise osv.except_osv('Error', 'The student {0} has {1} delayed bills'.format(sn, diff))

    def _should_be_billed(self, cr, uid, enroll_id, from_date, to_date):
        if not enroll_id and not from_date and not to_date:
            return False
        bill_pool = self.pool.get('pedagogy.billing')
        enroll_pool = self.pool.get('pedagogy.enrollment')
        enroll = enroll_pool.browse(cr, uid, enroll_id)

        if enroll.residual < 0.01 and not enroll.process:
            return False

        if from_date > enroll.contract_date_end:
            return False

        this_month = datetime.strptime(from_date, DATE_FORMAT).date()
        start_month = self._generate_reverse_billing_period(enroll, this_month)
        has_paid = self._get_payments_for_period(cr, uid, enroll, start_month, to_date)

        if has_paid and enroll.process:
            return True

        return not has_paid

    #
    #        past_dates = []
    #        for billing_date in schedule:
    #            if billing_date < this_month:
    #                past_dates.append(billing_date)
    #            elif billing_date > this_month: #Current month is not to be billed
    #                return False
    #            else:
    #                return self._verify_past_dates(cr, uid, enroll, past_dates)#self._have_prs(cr, uid, bill)

    def compute_sheet(self, cr, uid, ids, context=None):
        student_pool = self.pool.get('res.partner')
        bill_pool = self.pool.get('pedagogy.billing')
        run_pool = self.pool.get('pedagogy.billing.run')
        bill_ids = []
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, context=context)[0]
        run_data = {}
        if context and context.get('active_id', False):
            run_data = run_pool.read(cr, uid, context['active_id'], ['date_start', 'date_end', 'credit_note', 'month'])
        from_date = run_data.get('date_start', False)
        to_date = run_data.get('date_end', False)
        credit_note = run_data.get('credit_note', False)
        month = run_data.get('month', False)
        if not data['student_ids']:
            raise osv.except_osv(_('Warning !'), _('You must select students(s) to generate bill(s)'))
        for student in student_pool.browse(cr, uid, data['student_ids'], context=context):
            # contract_ids = self.get_student_contract(cr, uid, student_id, date_from, date_to, context=context)
            # for invoicee
            # see by residual
            # self.get_months(cr, uid, from_date, to_date)
            # see by billings confirmed
            # enrolls = bill_pool.search(cr, uid, [('state','=', 'confirmed'),])
            # invoicees = bill_pool._get_invoicees(cr, uid, [], student, from_date, to_date, context)
            enrolls = bill_pool.get_student_enrollment(cr, uid, student, False, False, from_date, to_date,
                                                       context=context)
            if enrolls:
                for enroll_id in enrolls:
                    if not self._should_be_billed(cr, uid, enroll_id, from_date, to_date):
                        continue
                    context.update({'enrollment_id': True})
                    bill_data = bill_pool.onchange_student_id(cr, uid, [], from_date, to_date, student.id, enroll_id,
                                                              context=context)
                    res = {
                        'student_id': student.id,
                        'invoicee_id': bill_data['value'].get('invoicee_id', False),
                        'name': bill_data['value'].get('name', False),
                        'struct_id': bill_data['value'].get('struct_id', False),
                        'enrollment_id': bill_data['value'].get('enrollment_id', False),
                        'run_id': context.get('active_id', False),
                        'input_line_ids': [(0, 0, x) for x in bill_data['value'].get('input_line_ids', False)],
                        'worked_days_line_ids': False,
                        'date_from': from_date,
                        'date_to': to_date,
                        'credit_note': credit_note,
                        'payment_term_id': student.property_payment_term.id or bill_data['value'].get('payment_term_id',
                                                                                                      False),
                        'month': month,
                    }
                    bill_ids.append(bill_pool.create(cr, uid, res, context=context))
            bill_pool.pedagogy_compute_sheet(cr, uid, bill_ids, context=context)
        return {'type': 'ir.actions.act_window_close'}
