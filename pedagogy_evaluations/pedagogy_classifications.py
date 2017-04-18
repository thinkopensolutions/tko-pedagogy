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

from osv import osv, fields
from tools.translate import _


class factor_evaluation_student(osv.osv):
    _name = 'pedagogy.factor.evaluation.student'

    def _get_name(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for factor_evaluation_student in self.browse(cr, uid, ids):
            if factor_evaluation_student.factor_evaluation_student_id:
                res[
                    factor_evaluation_student.id] = factor_evaluation_student.factor_evaluation_student_id.evaluation_id.description
            else:
                res[factor_evaluation_student.id] = factor_evaluation_student.factor_evaluation_id.factor_id.name
        return res

    def _get_description(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for factor_evaluation_student in self.browse(cr, uid, ids):
            if factor_evaluation_student.factor_evaluation_student_id:
                res[
                    factor_evaluation_student.id] = factor_evaluation_student.factor_evaluation_student_id.evaluation_id.name
            else:
                res[factor_evaluation_student.id] = factor_evaluation_student.factor_evaluation_id.description
        return res

    _columns = {
        'name': fields.function(_get_name, method=True, type='char', string='Name'),
        'evaluation_student_id': fields.many2one('pedagogy.evaluation.student', 'Evaluation/Student', required=True,
                                                 ondelete='cascade'),
        'factor_evaluation_id': fields.many2one('pedagogy.factor.evaluation', 'Factor'),
        'factor_evaluation_student_id': fields.many2one('pedagogy.evaluation.student', 'Evaluation Factor'),
        'description': fields.function(_get_description, method=True, type='char', string='Description'),
        'percentage': fields.related('factor_evaluation_id', 'percentage', type='float', readonly=True,
                                     string='Percentage'),
        'classification': fields.float('Classification'),
    }


class evaluation_student(osv.osv):
    _name = 'pedagogy.evaluation.student'

    def action_get_factors(self, cr, uid, ids, context={}):
        factor_evaluation_student = self.pool.get('pedagogy.factor.evaluation.student')
        evaluations = self.pool.get('pedagogy.evaluations')
        for evaluation_student in self.browse(cr, uid, ids):

            # remove existent factor_evaluation_student
            # I put uid=1=admin to be able to remove the old factors before get them again 
            factor_evaluation_student.unlink(cr, 1, [f.id for f in evaluation_student.factor_evaluation_student_ids])

            for factor in evaluation_student.evaluation_id.factor_ids:
                values = {
                    'evaluation_student_id': evaluation_student.id,
                    'factor_evaluation_id': factor.id,
                }
                # get the evaluation_student evaluation or give an error if doesn't exist
                # one must create the leafs evaluations before summative ones
                if factor.factor_evaluation_id:
                    factor_evaluation_student_not_approved_ids = self.search(cr, uid, [
                        ('evaluation_id', '=', factor.factor_evaluation_id.id),
                        ('student_id', '=', evaluation_student.student_id.id),
                        ('state', '<>', 'approved')])
                    factor_evaluation_student_id = self.search(cr, uid,
                                                               [('evaluation_id', '=', factor.factor_evaluation_id.id),
                                                                ('student_id', '=', evaluation_student.student_id.id),
                                                                ('state', '=', 'approved')])
                    if not factor_evaluation_student_id or factor_evaluation_student_not_approved_ids:
                        raise osv.except_osv('Warning',
                                             'Earlier evaluations for this student are missing or not approved. Create or confirm them first.')
                    else:
                        f_e_s = self.read(cr, uid, factor_evaluation_student_id[0],
                                          ['evaluation_id', 'final_classification', 'teacher_classification',
                                           'arithmetic_classification'])
                        evaluation = evaluations.read(cr, uid, f_e_s['evaluation_id'][0], ['description'])
                        values['factor_evaluation_student_id'] = factor_evaluation_student_id[0]
                        values['classification'] = f_e_s['final_classification'] or f_e_s['teacher_classification'] or \
                                                   f_e_s['arithmetic_classification']

                factor_evaluation_student.create(cr, uid, values)

        return True

    def _get_values(self, obj):
        values = {}
        for factor_eval in obj.factor_evaluation_student_ids:
            values[factor_eval.factor_evaluation_id.name] = factor_eval.classification
        return values

    def onchange_date_start(self, cr, uid, ids, date_start=False, evaluation_id=False, context=None):
        if not date_start and not evaluation_id:
            return {}
        evaluation_obj = self.pool.get('pedagogy.evaluations')
        evaluation_id = evaluation_obj.browse(cr, uid, evaluation_id)
        if evaluation_id:
            evaluation_date_start = evaluation_id.date_start
            evaluation_date_end = evaluation_id.date_end
            if date_start < evaluation_date_start or date_start > evaluation_date_end + ' 23:59:59':
                raise osv.except_osv(_('Invalid Date!'),
                                     _('The date must be inserted in range of the selected evaluation.'))
        return {}

    def onchange_date_end(self, cr, uid, ids, date_end=False, evaluation_id=False, context=None):
        if not date_end and not evaluation_id:
            return {}
        evaluation_obj = self.pool.get('pedagogy.evaluations')
        evaluation_id = evaluation_obj.browse(cr, uid, evaluation_id)
        if evaluation_id:
            evaluation_date_start = evaluation_id.date_start
            evaluation_date_end = evaluation_id.date_end
            if date_end < evaluation_date_start or date_end > evaluation_date_end + ' 23:59:59':
                raise osv.except_osv(_('Invalid Date!'),
                                     _('The date must be inserted in range of the selected evaluation.'))
        return {}

    def _verify_dates(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids):
            try:
                assert obj.date_start <= obj.date_end
                assert obj.date_start >= obj.class_year_id.year_id.date_start
                assert obj.date_end <= obj.class_year_id.year_id.date_end + ' 23:59:59'
            except AssertionError:
                raise osv.except_osv(_('Error'), _(
                    'The dates are wrong: verify if start date before end or must be in the selected class School Year!'))
        return True

    #    def _verify_factors(self, obj):
    #        our_factors = set(f.name for f in obj.factor_evaluation_student_ids)
    #        valid_factors = set(f.name or 'Evaluation' for f in obj.evaluation_id.factor_ids)
    #        missing = valid_factors - our_factors
    #        extra = our_factors - valid_factors
    #        if missing:
    #            raise osv.except_osv('Impossible', 'There are factors missing from the list! Please run Get Factors to update it.')
    #        elif extra:
    #            raise osv.except_osv('Impossible', 'There are outdated factors in the list! Please run Get Factors to update it.')

    def action_calculate(self, cr, uid, ids, context={}):
        for obj in self.browse(cr, uid, ids):
            #            self._verify_factors(obj)
            grade = 0.0
            for f_e_s in obj.factor_evaluation_student_ids:
                grade += f_e_s.classification * (f_e_s.percentage / 100.0)
            self.write(cr, uid, obj.id, {
                'arithmetic_classification': grade,
                'teacher_classification': grade,
                'final_classification': grade
            })
        return True

    def onchange_filter_students(self, cr, uid, ids, evaluation_id, context=None):
        res = {}
        if evaluation_id:
            evaluation = self.pool.get('pedagogy.evaluations').browse(cr, uid, evaluation_id)
            student_ids = [enrollment.student_id.id for enrollment in evaluation.class_year_id.enrollment_ids]
            if evaluation:
                res = {'value': {'date_start': evaluation['date_start'],
                                 'date_end': evaluation['date_end']}}
            res['domain'] = {'student_id': [('id', 'in', student_ids)]}
        return res

    def check_factors(self, cr, uid, ids, *args):
        for obj in self.browse(cr, uid, ids):
            if not obj.factor_evaluation_student_ids:
                raise osv.except_osv('Warning', 'You cannot confirm without factors.')
        return True

    def write_history(self, cr, uid, ids, *args):
        for obj in self.browse(cr, uid, ids):
            self.pool.get('pedagogy.classification.history').create(cr, uid, {'evaluation_student_id': obj.id,
                                                                              'user_id': uid,
                                                                              'date': datetime.now().strftime(
                                                                                  '%Y-%m-%d %H:%M:%S'),
                                                                              'change': obj.state}
                                                                    )
        return True

    def _get_evaluation_student(self, cr, uid, ids, context=None):
        return self.pool.get('pedagogy.evaluation_student').search(cr, uid, [('evaluation_id', 'in', ids)],
                                                                   context=context)

    _columns = {
        'state': fields.selection([('draft', _('Draft')),
                                   ('confirmed', _('Confirmed')),
                                   ('suspended', _('Suspended')),
                                   ('approved', _('Approved'))], 'State', required=True, readonly=True),
        'student_id': fields.many2one('res.partner', 'Student', required=True, domain=[('is_student', '=', True)]),
        'evaluation_id': fields.many2one('pedagogy.evaluations', 'Evaluation', required=True),
        'is_summative': fields.related('evaluation_id', 'type_id', 'is_summative', type='boolean', string='Summative'),
        'type_id': fields.related('evaluation_id', 'type_id', type='many2one', relation='pedagogy.evaluations.type',
                                  string='Type'),
        'factor_evaluation_student_ids': fields.one2many('pedagogy.factor.evaluation.student', 'evaluation_student_id',
                                                         'Factor/Evaluation', required=True),
        'history_ids': fields.one2many('pedagogy.classification.history', 'evaluation_student_id', 'History'),
        'year_id': fields.related('evaluation_id', 'class_year_id', 'year_id', type='many2one',
                                  relation='pedagogy.school.year', string='Year'),
        'date_start': fields.datetime('Start Date', required=True),
        'date_end': fields.datetime('End Date', required=True),
        'arithmetic_classification': fields.float('Arithmetic Classification', readonly=True),
        'teacher_classification': fields.float('Teacher Classification'),
        'final_classification': fields.float('Final Classification', write=['pedagogy_base.group_pedagogy_pedagogy']),
        'teacher_observations': fields.text('Teacher observations'),
        'other_observations': fields.text('Other observations'),
    }

    _sql_constraints = [
        ('evaluation_uniq', 'unique(student_id, evaluation_id)',
         'The student already has a classification for this evaluation!'),
    ]

    _defaults = {'state': 'draft',
                 'arithmetic_classification': 0,
                 'teacher_classification': 0,
                 'final_classification': 0,
                 # to prevent from appearing a false in from this field in view if field empty
                 'teacher_observations': ' ',
                 'other_observations': ' ',
                 }

    _order = 'date_start asc'


class pedagogy_enrollment_history(osv.osv):
    _name = 'pedagogy.classification.history'
    _description = 'Classification History'

    _columns = {
        'evaluation_student_id': fields.many2one('pedagogy.evaluation.student', 'Evaluation', ondelete='cascade',
                                                 required=True),
        'user_id': fields.many2one('res.users', 'User', ondelete='cascade', required=True),
        'date': fields.datetime('Date', required=True),
        'change': fields.char('Change', size=128, required=True),
        }

    _order = 'date desc'
