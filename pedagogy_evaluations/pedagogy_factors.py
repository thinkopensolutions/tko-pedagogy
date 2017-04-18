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

from openerp.osv import osv, fields


class pedagogy_factor(osv.osv):
    _name = 'pedagogy.factor'
    _columns = {
        'name': fields.char('Name', size=64),
        'description': fields.char('Description', size=256)
    }


class pedagogy_factor_evaluation(osv.osv):
    _name = 'pedagogy.factor.evaluation'

    def _get_description(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for factor_evaluation in self.browse(cr, uid, ids):
            if factor_evaluation.factor_evaluation_id:
                res[factor_evaluation.id] = factor_evaluation.factor_evaluation_id.description
            else:
                res[factor_evaluation.id] = factor_evaluation.factor_id.description
        return res

    _columns = {
        'name': fields.related('factor_id', 'name', type='char', string='Description', readonly=True),
        'evaluation_id': fields.many2one('pedagogy.evaluations', 'Evaluation', required=True, ondelete='cascade'),
        'is_summative': fields.related('evaluation_id', 'type_id', 'is_summative', type='boolean',
                                       string='Is Summative', readonly=True),
        'class_discipline_teacher_id': fields.related('evaluation_id', 'class_discipline_teacher_id', type='many2one',
                                                      relation='pedagogy.class.discipline.teacher',
                                                      string='Class Discipline Teacher', readonly=True),
        'factor_id': fields.many2one('pedagogy.factor', 'Factor'),
        'factor_evaluation_id': fields.many2one('pedagogy.evaluations', 'Evaluation Note'),
        'description': fields.function(_get_description, method=True, type='char', string='Description'),
        'percentage': fields.float('Percentage', required=True)
    }

    _sql_constraints = [
        ('exist', 'check(factor_evaluation_id is not null or factor_id is not null)',
         'You must have a factor or a related evaluation in each line!'),
        ('one_per_line', 'check(factor_evaluation_id is null or factor_id is null)',
         'You cannot have a factor and a related evaluation in the same line!'),
        ('factor_uniq', 'unique(factor_id, evaluation_id)', 'Factor must be unique per evaluation!'),
        ('factor_evaluation_uniq', 'unique(factor_evaluation_id, evaluation_id)',
         'Referenced evaluation must be unique per evaluation!'),
    ]
