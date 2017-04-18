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

import tools
from osv import fields, osv


class evaluations_report(osv.osv):
    _name = 'pedagogy.evaluations.report'
    _description = 'evaluations Report'
    _auto = False

    _columns = {
        'year_id': fields.many2one('pedagogy.school.year', 'Year', readonly=True),
        'area_id': fields.many2one('pedagogy.group.area', 'Area', readonly=True),
        'group_id': fields.many2one('pedagogy.group', 'Group', readonly=True),
        'class_id': fields.many2one('pedagogy.class', 'Class', readonly=True),
        'discipline_id': fields.many2one('pedagogy.discipline', 'Discipline', readonly=True),
        'teacher_id': fields.many2one('hr.employee', 'Teacher', readonly=True),
        'student_id': fields.many2one('res.partner', 'Student', domain=[('is_student', '=', True)], readonly=True),
        'discipline_area_id': fields.many2one('pedagogy.discipline_area', 'Discipline Area', readonly=True),
        'evaluation_type_id': fields.many2one('pedagogy.evaluations.type', 'Evaluation Type', readonly=True),
        'arithmetic_note': fields.integer('NA', readonly=True, group_operator='avg'),
        'teacher_note': fields.integer('NP', readonly=True, group_operator='avg'),
        'final_note': fields.integer('NF', readonly=True, group_operator='avg'),
        'date_start': fields.date('Start Date', readonly=True),
    }
    _order = 'year_id desc'

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'pedagogy_evaluations_report')
        cr.execute('''
            create or replace view pedagogy_evaluations_report as (
            select
                classif.id as id,
                cl_year.year_id as year_id,
                g.group_area_id as area_id,
                cl.group_id as group_id,
                cl_year.class_id as class_id,
                cdt.discipline_id as discipline_id,
                cdt.teacher_id as teacher_id,
                classif.student_id as student_id,
                disc.discipline_area_id as discipline_area_id,
                classif.arithmetic_classification as arithmetic_note,
                classif.teacher_classification as teacher_note,
                classif.final_classification as final_note,
                year.date_start as date_start
            from
                pedagogy_evaluation_student classif
                left join pedagogy_evaluations eval on (classif.evaluation_id = eval.id) 
                left join pedagogy_class_discipline_teacher cdt on (eval.class_discipline_teacher_id = cdt.id)
                left join pedagogy_class_year cl_year on (cdt.class_year_id = cl_year.id)
                left join pedagogy_school_year year on (cl_year.year_id = year.id)
                left join pedagogy_class cl on (cl_year.class_id = cl.id)
                left join pedagogy_group g on (cl.group_id = g.id)
                left join pedagogy_discipline disc on (cdt.discipline_id = disc.id)
            );
            create rule evaluations_report_del as on delete to pedagogy_evaluations_report
            do instead delete from pedagogy_evaluation_student where id = OLD.id;
        ''')
