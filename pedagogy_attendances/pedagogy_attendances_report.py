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

from openerp import tools
from openerp.osv import osv, fields


class pedagogy_attendances_report(osv.osv):
    _name = 'pedagogy.attendances.report'
    _description = 'Attendances Report'
    _auto = False

    _columns = {
        'enrollment_id': fields.many2one('pedagogy.enrollment', 'Number', required=True),
        'student_id': fields.many2one('res.partner', 'Student', required=True),
        'year_id': fields.many2one('pedagogy.school.year', 'Year', required=True),
        'area_id': fields.many2one('pedagogy.discipline_area', 'Area', required=True),
        'group_id': fields.many2one('pedagogy.group.area', 'Group', required=True),
        'class_id': fields.many2one('pedagogy.class', 'Class', required=True),
        'discipline_id': fields.many2one('pedagogy.discipline', 'Discipline', required=True),
        'teacher_id': fields.many2one('hr.employee', 'Teacher', required=True),
        'state': fields.selection([
            ('unknown', 'Unknown'),
            ('present', 'Present'),
            ('unjustified', 'Unjustified'),
            ('justified', 'Justified'),
        ], 'State', required=True),
        'date': fields.date('Date', required=True),
    }

    def init(self, cr):
        tools.sql.drop_view_if_exists(cr, 'pedagogy_attendances_report')
        cr.execute('''
            CREATE or REPLACE view pedagogy_attendances_report as (
                    SELECT  
                        psa.id as id
                        ,psa.enrollment_id as enrollment_id
                        ,pe.student_id as student_id
                        ,pcy.year_id as year_id 
                        ,pd.discipline_area_id as area_id
                        ,pc.group_id as group_id
                        ,pcy.class_id as class_id
                        ,pcdt.discipline_id as discipline_id
                        ,pcdt.teacher_id as teacher_id
                        ,psah.date as date
                        ,psa.state as state
                    FROM
                        pedagogy_student_attendance psa
                        INNER JOIN pedagogy_enrollment pe on pe.id = psa.enrollment_id
                        INNER JOIN pedagogy_class_year pcy on pcy.id = pe.class_year_id
                        INNER JOIN pedagogy_time_table ptt on ptt.id = psa.time_table_id
                        INNER JOIN pedagogy_class_discipline_teacher pcdt on pcdt.id = ptt.class_discipline_teacher_id
                        INNER JOIN pedagogy_discipline pd on pd.id = pcdt.discipline_id
                        INNER JOIN pedagogy_class pc on pc.id = pcy.class_id
                        INNER JOIN pedagogy_student_attendance_history psah on psah.attendance_id = psa.id
                    )
        ''')
