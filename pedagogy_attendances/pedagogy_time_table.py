# # -*- coding: utf-8 -*-
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

from openerp.osv import osv, fields

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
DATE_FORMAT = '%Y-%m-%d'


class pedagogy_time_table(osv.osv):
    _inherit = 'pedagogy.time_table'

    def update_attendance_sheet(self, cr, uid, ids, context=None):
        attendence_obj = self.pool.get('pedagogy.student.attendance')
        attendances_ids = []
        for line in self.browse(cr, uid, ids):
            # delete old attendance records
            for atendance in line.pedagogy_student_attendance_ids:
                attendence_obj.unlink(cr, uid, atendance.id)
            class_year = line.class_discipline_teacher_id.class_year_id
            if class_year:
                class_start = datetime.strptime(class_year.year_id.date_start, DATE_FORMAT).date()
                class_end = datetime.strptime(class_year.year_id.date_end, DATE_FORMAT).date()
                line_start = datetime.strptime(line.date_from, DATETIME_FORMAT).date()
                line_end = datetime.strptime(line.date_to, DATETIME_FORMAT).date()
                if line_start >= class_start and line_end <= class_end:
                    for enrollment in class_year.enrollment_ids:
                        if enrollment.state == 'enrolled':
                            # create new attendance records
                            values = {
                                'student_id': enrollment.student_id.id,
                                'enrollment_id': enrollment.id,
                                'time_table_id': line.id
                            }
                            id = attendence_obj.create(cr, uid, values)
                            attendances_ids.append(id)
        return {'value': {'pedagogy_student_attendance_ids': attendances_ids}}

    # remove student attendances when copy
    def copy(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        default.update({
            'pedagogy_student_attendance_ids': False,
        })
        return super(pedagogy_time_table, self).copy(cr, uid, id, default, context)

    _columns = {
        'pedagogy_student_attendance_ids': fields.one2many('pedagogy.student.attendance', 'time_table_id',
                                                           'Student Attendance'),
    }
