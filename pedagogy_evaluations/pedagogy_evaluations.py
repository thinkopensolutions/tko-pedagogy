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
from tools.translate import _


class pedagogy_evaluations_type(osv.osv):
    _name = 'pedagogy.evaluations.type'

    _columns = {
        'name': fields.char('Evaluation Type', size=64, required=True),
        'is_summative': fields.boolean('Is Summative?'),
    }

    _order = 'name asc'


class pedagogy_evaluations(osv.osv):
    _name = 'pedagogy.evaluations'

    def create(self, cr, uid, vals, context=None):
        if context and 'class_year_copy' in context:
            return None
        return super(pedagogy_evaluations, self).create(cr, uid, vals, context=context)

    def _verify_factors(self, cr, uid, ids, context=None):
        for evaluation in self.browse(cr, uid, ids):
            percentages = [factor.percentage for factor in evaluation.factor_ids]
            if len(percentages) > 0 and sum(percentages) < 100:
                raise osv.except_osv(_('Invalid factor'), _('The factors must sum 100% or more'))
        return True

    def onchange_get_dates_from_year(self, cr, uid, ids, cdt_id, date_start, date_end, context=None):
        result = {}
        if cdt_id:
            cdt = self.pool.get('pedagogy.class.discipline.teacher').browse(cr, uid, [cdt_id])
            result = {'value': {'date_start': cdt[0]['date_start'],
                                'date_end': cdt[0]['date_end']}}
        return result

    def onchange_date_start(self, cr, uid, ids, date_start=False, class_discipline_teacher_id=False, context=None):
        if not date_start and not class_discipline_teacher_id:
            return {}
        cdt_obj = self.pool.get('pedagogy.class.discipline.teacher')
        cdt_id = cdt_obj.browse(cr, uid, class_discipline_teacher_id)
        if cdt_id:
            cdt_date_start = cdt_id.date_start
            cdt_date_end = cdt_id.date_end
            if date_start < cdt_date_start or date_start > cdt_date_end + ' 23:59:59':
                raise osv.except_osv(_('Invalid Date!'), _('The date must be inserted in range of the selected class.'))
        return {}

    def onchange_date_end(self, cr, uid, ids, date_end=False, class_discipline_teacher_id=False, context=None):
        if not date_end and not class_discipline_teacher_id:
            return {}
        cdt_obj = self.pool.get('pedagogy.class.discipline.teacher')
        cdt_id = cdt_obj.browse(cr, uid, class_discipline_teacher_id)
        if cdt_id:
            cdt_date_start = cdt_id.date_start
            cdt_date_end = cdt_id.date_end
            if date_end < cdt_date_start or date_end > cdt_date_end + ' 23:59:59':
                raise osv.except_osv(_('Invalid Date!'), _('The date must be inserted in range of the selected class.'))
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

    def _get_name(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for evaluation in self.browse(cr, uid, ids):
            class_name = evaluation.class_discipline_teacher_id.name
            res[evaluation.id] = u'{0} / {1}'.format(evaluation.description, class_name)
        return res

    def _evaluation_search(self, cr, uid, obj, name, args, context):
        res = []
        query = 'SELECT pedagogy_evaluations.id \
                        FROM \
                            pedagogy_evaluations \
                        WHERE \
                            pedagogy_evaluations.name ilike %s'
        cr.execute(query, ('%' + args[0][2] + '%',))
        res = [('id', 'in', cr.fetchall())]
        return res

    def _get_evaluation_years(self, cr, uid, ids, context=None):
        evaluations = []
        classes_years = self.pool.get('pedagogy.class.year').search(cr, uid, [('year_id', 'in', ids)], context=context)
        cdts = self.pool.get('pedagogy.class.discipline.teacher').search(cr, uid,
                                                                         [('class_year_id', 'in', classes_years)],
                                                                         context=context)
        evaluations = self.pool.get('pedagogy.evaluations').search(cr, uid,
                                                                   [('class_discipline_teacher_id', 'in', cdts)],
                                                                   context=context)
        return evaluations

    def _get_evaluation_classes(self, cr, uid, ids, context=None):
        evaluations = []
        classes_years = self.pool.get('pedagogy.class.year').search(cr, uid, [('class_id', 'in', ids)], context=context)
        cdts = self.pool.get('pedagogy.class.discipline.teacher').search(cr, uid,
                                                                         [('class_year_id', 'in', classes_years)],
                                                                         context=context)
        evaluations = self.pool.get('pedagogy.evaluations').search(cr, uid,
                                                                   [('class_discipline_teacher_id', 'in', cdts)],
                                                                   context=context)
        return evaluations

    def _get_evaluation_classes_years(self, cr, uid, ids, context=None):
        evaluations = []
        cdts = self.pool.get('pedagogy.class.discipline.teacher').search(cr, uid, [('class_year_id', 'in', ids)],
                                                                         context=context)
        evaluations = self.pool.get('pedagogy.evaluations').search(cr, uid,
                                                                   [('class_discipline_teacher_id', 'in', cdts)],
                                                                   context=context)
        return evaluations

    def _get_evaluation_disciplines(self, cr, uid, ids, context=None):
        evaluations = []
        cdts = self.pool.get('pedagogy.class.discipline.teacher').search(cr, uid, [('discipline_id', 'in', ids)],
                                                                         context=context)
        evaluations = self.pool.get('pedagogy.evaluations').search(cr, uid,
                                                                   [('class_discipline_teacher_id', 'in', cdts)],
                                                                   context=context)
        return evaluations

    def _get_evaluation_teachers(self, cr, uid, ids, context=None):
        evaluations = []
        teachers = self.pool.get('hr.employee').search(cr, uid, [('resource_id', 'in', ids)], context=context)
        cdts = self.pool.get('pedagogy.class.discipline.teacher').search(cr, uid, [('teacher_id', 'in', teachers)],
                                                                         context=context)
        evaluations = self.pool.get('pedagogy.evaluations').search(cr, uid,
                                                                   [('class_discipline_teacher_id', 'in', cdts)],
                                                                   context=context)
        return evaluations

    def _get_evaluation_cdts(self, cr, uid, ids, context=None):
        evaluations = []
        evaluations = self.pool.get('pedagogy.evaluations').search(cr, uid,
                                                                   [('class_discipline_teacher_id', 'in', ids)],
                                                                   context=context)
        return evaluations

    _columns = {
        'name': fields.function(_get_name, fnct_search=_evaluation_search,
                                store={
                                    'pedagogy.evaluations': (lambda self, cr, uid, ids, c={}: ids,
                                                             ['description', 'class_discipline_teacher_id'], 10),
                                    'pedagogy.class.discipline.teacher': (
                                    _get_evaluation_cdts, ['class_year_id', 'discipline_id', 'teacher_id'], 20),
                                    'pedagogy.school.year': (_get_evaluation_years, ['name'], 40),
                                    'pedagogy.class': (_get_evaluation_classes, ['name'], 40),
                                    'pedagogy.class.year': (_get_evaluation_classes_years, ['year_id', 'class_id'], 30),
                                    'pedagogy.discipline': (_get_evaluation_disciplines, ['name'], 30),
                                    'resource.resource': (_get_evaluation_teachers, ['name'], 40),
                                },
                                method=True, type='char', string='Name'),
        'description': fields.char('Description', size=254, required=True),
        'type_id': fields.many2one('pedagogy.evaluations.type', 'Type', required=True),
        'class_discipline_teacher_id': fields.many2one('pedagogy.class.discipline.teacher', 'Class Discipline Teacher',
                                                       required=True),
        'class_year_id': fields.related('class_discipline_teacher_id', 'class_year_id', type='many2one',
                                        relation='pedagogy.class.year', string='Class Year'),
        'class_id': fields.related('class_year_id', 'class_id', type='many2one', relation='pedagogy.class',
                                   string='Class'),
        'year_id': fields.related('class_year_id', 'year_id', type='many2one', relation='pedagogy.school.year',
                                  string='Year'),
        'teacher_id': fields.related('class_discipline_teacher_id', 'teacher_id', type='many2one',
                                     relation='hr.employee', string='Teacher'),
        'discipline_id': fields.related('class_discipline_teacher_id', 'discipline_id', type='many2one',
                                        relation='pedagogy.discipline', string='Discipline'),
        'date_start': fields.datetime('Start Date', required=True),
        'date_end': fields.datetime('End Date', required=True),
        'observations': fields.text('Observations'),
        'factor_ids': fields.one2many('pedagogy.factor.evaluation', 'evaluation_id', 'Factors'),
    }

    _constraints = [
        (_verify_factors, 'Invalid Factors', ['factor_ids']),
        (_verify_dates, 'Invalid Dates', ['date_start', 'date_end']),
    ]

    # to prevent from appearing a false in from this field in view if field empty
    _defaults = {'observations': ' '}

    _order = 'date_end, name'
