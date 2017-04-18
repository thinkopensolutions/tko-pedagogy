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

import logging
from datetime import datetime, date
from lxml.builder import E

from lxml.etree import tostring as xml_to_string
from openerp import _
from openerp.osv import osv, fields

DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
FACTOR_SEPARATOR = u'_'


class classifications_matrix_selection(osv.osv_memory):
    _name = 'pedagogy.classifications.matrix.selection'

    _columns = {
        'evaluation_id': fields.many2one('pedagogy.evaluations', 'Evaluation', required=True),
        'class_year_discipline_teacher_id': fields.related('evaluation_id', 'class_discipline_teacher_id',
                                                           type='many2one',
                                                           relation='pedagogy.class.discipline.teacher',
                                                           string='Class/Discipline/Teacher'),
        'class_year_id': fields.related('class_year_discipline_teacher_id', 'class_year_id', type='many2one',
                                        relation='pedagogy.class.year', string='Class'),
        'discipline_id': fields.related('class_year_discipline_teacher_id', 'discipline_id', type='many2one',
                                        relation='pedagogy.discipline', string='Discipline'),
        'teacher_id': fields.related('class_year_discipline_teacher_id', 'teacher_id', type='many2one',
                                     relation='hr.employee', string='Teacher'),
        'all_evaluations': fields.boolean('All Evaluations'),
    }

    #    def get_teacher_from_user(self, cr, uid):
    #        teachers_pool = self.pool.get('hr.employee')
    #        try:
    #            query = [('user_id', '=', uid), ('is_teacher','=',True)]
    #            teachers_ids = teachers_pool.search(cr, uid, query)
    #            [teacher] = teachers_pool.browse(cr, uid, teachers_ids)
    #            return teacher
    #        except ValueError:
    #            raise osv.except_osv(_('Error'), _('There\'s either no or more than one teacher associated with this user'))

    #    def find_cdt(self, cr, uid, class_year, discipline, teacher):
    #        cdt_pool = self.pool.get('pedagogy.class.discipline.teacher')
    #        query = [('class_year_id', '=', class_year.id),
    #                 ('discipline_id', '=', discipline.id),
    #                 ('teacher_id', '=', teacher.id)]
    #        try:
    #            cdt_ids = cdt_pool.search(cr, uid, query)
    #            [cdt] = cdt_pool.browse(cr, uid, cdt_ids)
    #            return cdt
    #        except ValueError:
    #            raise osv.except_osv(_('Error'), _('There\'s either no or more than one Class/Discipline/Teacher associated with these values'))

    def create_matrix(self, cr, uid, ids, context=None):
        for selection in self.browse(cr, uid, ids):
            return {
                'name': _(u'Classifications Matrix'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'pedagogy.classifications.matrix',
                'view_id': False,
                # 'target': 'new',
                'views': False,
                'type': 'ir.actions.act_window',
                'context': {'cdt': selection.evaluation_id.class_discipline_teacher_id.id},
            }


# teacher = selection.teacher_id
#            if not teacher:
#                teacher = self.get_teacher_from_user(cr, uid)
#            cdt = self.find_cdt(cr, uid, selection.class_year_id, selection.discipline_id, teacher)
#            return self.launch_matrix(cdt.id)
#            return self.launch_matrix()

#    def launch_matrix(self, cdt_id):
#        return {
#            'name': _(u'Classifications Matrix'),
#            'view_type': 'form',
#            'view_mode': 'form',
#            'res_model': 'pedagogy.classifications.matrix',
#            'view_id': False,
#            #'target': 'new',
#            'views': False,
#            'type': 'ir.actions.act_window',
#            'context': {'cdt': cdt_id},
#        }

class classifications_matrix(osv.osv_memory):
    _name = 'pedagogy.classifications.matrix'

    def load_cdt(self, cr, uid, cdt_id):
        cdt_pool = self.pool.get('pedagogy.class.discipline.teacher')
        try:
            cdt = cdt_pool.browse(cr, uid, [cdt_id])[0]
        except IndexError:
            raise osv.except_osv(_('Error'), _('There is no Class/Discipline/Teacher associated with this teacher'))
        return cdt

    def get_classifications_from_cdt(self, cr, uid, class_discipline_teacher_id):
        classif_pool = self.pool.get('pedagogy.evaluation.student')
        query = [('evaluation_id.class_discipline_teacher_id.id', '=', class_discipline_teacher_id.id)]
        classifications_ids = classif_pool.search(cr, uid, query)
        classifications = classif_pool.browse(cr, uid, classifications_ids)
        return classifications

    def calculate_total_columns(self, evaluations_factors):
        total = 2  # student column
        for evaluation, factors in evaluations_factors.items():
            total += 4  # for grades
            total += len(factors) * 2
        return total

    def is_pedagogical(self, cr, uid):
        user_pool = self.pool.get('res.users')
        is_pedagogical = any(
            True for group in user_pool.browse(cr, uid, uid).groups_id if group.name == u'Pedagogy / Pedagogical')
        return is_pedagogical

    def is_class_teacher(self, class_discipline_teacher_id, uid):
        return class_discipline_teacher_id.teacher_id.user_id.id == uid or uid == 1

    def generate_header(self, evaluations_factors):
        ''' The header has two lines: the first has the evaluation names, the
        second has the factors'''
        header = []
        header.append(E.label(string=_(u' '), colspan=u'2'))
        for evaluation, factors in evaluations_factors.items():
            size = 2 * len(factors) + 4
            header.append(E.label(string=evaluation.type_id.name, colspan=unicode(size)))
        header.append(E.newline())
        header.append(E.label(string=_(u' '), colspan=u'2'))
        for evaluation, factors in evaluations_factors.items():
            for factor in factors:
                header.append(E.label(string=factor.name, colspan=u'2'))
            header.append(E.label(string=u'TN', colspan=u'2'))
            header.append(E.label(string=u'FN', colspan=u'2'))
        header.append(E.newline())
        return header

    def build_evaluations_factors_tree(self, classifications):
        ''' Example of a tree:
            Evaluation 1:
                Factor 1
                Factor 2'''
        tree = {}
        for classification in classifications:
            evaluation = classification.evaluation_id
            if evaluation.name not in tree:
                tree[evaluation] = evaluation.factor_ids
        return tree

    def generate_name(self, student_id, evaluation_id, factor_id):
        keys = [student_id, evaluation_id, factor_id]
        return FACTOR_SEPARATOR.join(map(unicode, keys))

    def create_field(self, matrix, fields, name, readonly=False):
        modifiers = u'{\'readonly\': true}' if readonly else u''
        matrix.append(E.field(name=name,
                              nolabel=u'1',
                              colspan=u'2',
                              modifiers=modifiers))
        fields[name] = {'selectable': True,
                        'type': 'float',
                        'string': name,
                        'views': {},
                        'readonly': readonly}

    def is_past(self, evaluation):
        d = datetime.strptime(evaluation.date_end, DATE_FORMAT).date()
        return d < date.today()

    def generate_matrix(self, students, evaluations_factors, is_pedagogical, is_class_teacher):
        students = sorted(students, key=lambda s: s.name)
        matrix = []
        fields = {}
        for student in students:
            matrix.append(E.label(string=student.name, colspan=u'2'))
            for evaluation, factors in evaluations_factors.items():
                is_past = self.is_past(evaluation)
                for factor in factors:
                    name = self.generate_name(student.id, evaluation.id, factor.id)
                    self.create_field(matrix, fields, name, readonly=(is_past or not is_class_teacher))
                tn_name = self.generate_name(student.id, evaluation.id, 'TN')
                self.create_field(matrix, fields, tn_name, readonly=(is_past or not is_class_teacher))
                fn_name = self.generate_name(student.id, evaluation.id, 'FN')
                self.create_field(matrix, fields, fn_name, readonly=(is_past or not is_pedagogical))
            matrix.append(E.newline())
        return matrix, fields

    def generate_view(self, cr, uid, context):
        if not context or not 'cdt' in context:
            raise osv.except_osv('Unable to show matrix', 'Please reload the matrix using the menu')
        class_discipline_teacher = self.load_cdt(cr, uid, context['cdt'])
        classifications = self.get_classifications_from_cdt(cr, uid, class_discipline_teacher)
        is_pedagogical = self.is_pedagogical(cr, uid)
        is_class_teacher = self.is_class_teacher(class_discipline_teacher, uid)

        evaluations_factors = self.build_evaluations_factors_tree(classifications)
        students = set([classification.student_id for classification in classifications])

        total_columns = self.calculate_total_columns(evaluations_factors)
        group = E.group(col=unicode(total_columns), colspan=u'6', width='600px')
        header = self.generate_header(evaluations_factors)
        group.extend(header)
        matrix, fields = self.generate_matrix(students, evaluations_factors, is_pedagogical, is_class_teacher)
        group.extend(matrix)

        return E.form(group, width=u'600px'), fields

    def fields_view_get(self, cr, user, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        parent = super(classifications_matrix, self).fields_view_get(cr, user, view_id, view_type, context, toolbar,
                                                                     submenu)
        if view_type == 'form':
            xml, fields = self.generate_view(cr, user, context)
            xml = xml_to_string(xml)
            parent['arch'] = xml
            parent['fields'] = fields
        return parent

    def create(self, cr, uid, vals, context=None):
        id = super(classifications_matrix, self).create(cr, uid, {}, context=context)
        self.write(cr, uid, [id], vals, context=context)
        return id

    def write(self, cr, uid, ids, vals, context=None):
        for field, value in vals.items():
            student, evaluation, factor = field.split(FACTOR_SEPARATOR)
            student_id, evaluation_id = int(student), int(evaluation)
            if factor.isdigit():  # it's the ID of a factor
                factor_id = int(factor)
                self.write_to_factor(cr, uid, student_id, factor_id, value)
            else:  # it's a grade
                map = {'FN': 'final_classification', 'TN': 'teacher_classification'}
                field = map[factor]
                self.write_to_classification_field(cr, uid, student_id, evaluation_id, field, value)
        return True

    def write_to_factor(self, cr, uid, student_id, factor_id, value):
        pool = self.pool.get('pedagogy.factor.evaluation.student')
        query = [('evaluation_student.student.id', '=', student_id), ('factor_evaluation_id', '=', factor_id)]
        try:
            [factor_id] = pool.search(cr, uid, query)
            pool.write(cr, uid, factor_id, {'classification': value})
        except ValueError:
            logging.error('Factor {0} for student {1} not found'.format(factor_id, student_id))
            # raise osv.except_osv('Oh no', 'The factor wasn't found. This wasn't supposed to happen. Please call support')

    def write_to_classification_field(self, cr, uid, student_id, evaluation_id, field, value):
        pool = self.pool.get('pedagogy.evaluation.student')
        query = [('evaluation_id', '=', evaluation_id), ('student_id', '=', student_id)]
        try:
            [classification_id] = pool.search(cr, uid, query)
            pool.write(cr, uid, classification_id, {field: value})
        except ValueError:
            logging.error(
                'Classification for evaluation {0} for student {1} not found'.format(evaluation_id, student_id))
            raise osv.except_osv('Oh no',
                                 'The factor wasn\'t found. This wasn\'t supposed to happen. Please call support')

    def default_get(self, cr, uid, fields, context=None):
        [res] = self.read(cr, uid, [1], fields, context=context)
        del res['id']
        return res

    def read(self, cr, uid, ids, fields, context=None):
        res = {'id': ids[0]}
        for field in fields:
            student, evaluation, factor = field.split(FACTOR_SEPARATOR)
            student_id, evaluation_id = int(student), int(evaluation)
            if factor.isdigit():  # it's the ID of a factor
                factor_id = int(factor)
                res[field] = self.read_from_factor(cr, uid, student_id, factor_id)
            else:  # it's a grade
                map = {'FN': 'final_classification', 'TN': 'teacher_classification'}
                field_name = map[factor]
                res[field] = self.read_from_classification_field(cr, uid, student_id, evaluation_id, field_name)
        return [res]

    def read_from_factor(self, cr, uid, student_id, factor_id):
        pool = self.pool.get('pedagogy.factor.evaluation.student')
        query = [('evaluation_student_id.student_id.id', '=', student_id), ('factor_evaluation_id', '=', factor_id)]
        try:
            [factor_id] = pool.search(cr, uid, query)
            return pool.read(cr, uid, factor_id, ['classification'])['classification']
        except ValueError:
            return None

    def read_from_classification_field(self, cr, uid, student_id, evaluation_id, field):
        pool = self.pool.get('pedagogy.evaluation.student')
        query = [('evaluation_id', '=', evaluation_id), ('student_id', '=', student_id)]
        try:
            [classification_id] = pool.search(cr, uid, query)
            return pool.read(cr, uid, classification_id, [field])[field]
        except ValueError:
            return None

    _columns = {}
