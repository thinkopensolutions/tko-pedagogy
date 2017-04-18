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

from openerp.osv import osv, fields


class pedagogy_student_attendance(osv.osv):
    _name = 'pedagogy.student.attendance'
    _description = 'Pedagogy Student Attendance'

    def write(self, cr, uid, ids, vals, context=None):
        res = super(pedagogy_student_attendance, self).write(cr, uid, ids, vals, context=context)
        for line in self.browse(cr, uid, ids):
            if vals.has_key('state'):
                self.pool.get('pedagogy.student.attendance.history').create(cr, uid, {
                    'attendance_id': line.id,
                    'user_id': uid,
                    'student_id': line.student_id.id,
                    'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'change': line.state,
                })
        return res

    def set_present(self, cr, uid, ids, *args):
        for line in self.browse(cr, uid, ids):
            res = self.write(cr, uid, [line.id], {'state': 'present'} or False)
        return res

    def set_unjustified(self, cr, uid, ids, *args):
        for line in self.browse(cr, uid, ids):
            res = self.write(cr, uid, [line.id], {'state': 'unjustified'} or False)
        return res

    def set_justified(self, cr, uid, ids, *args):
        for line in self.browse(cr, uid, ids):
            res = self.write(cr, uid, [line.id], {'state': 'justified'} or False)
        return res

    def onchange_time_table(self, cr, uid, ids, time_table_id=False, context=None):
        res = {}
        if time_table_id:
            time_table_obj = self.pool.get('pedagogy.time_table')
            time_table = time_table_obj.browse(cr, uid, time_table_id)
            res = {'value': {'class_discipline_teacher_id': time_table.class_discipline_teacher_id.id}}
        return res

    def onchange_enrollment(self, cr, uid, ids, enrollment_id=False, context=None):
        res = {}
        if enrollment_id:
            enrollment_obj = self.pool.get('pedagogy.enrollment')
            enrollment = enrollment_obj.browse(cr, uid, enrollment_id)
            res = {'value': {'student_id': enrollment.student_id.id}}
        return res

    _columns = {
        'state': fields.selection([('unknown', 'Unknown'),
                                   ('present', 'Present'),
                                   ('unjustified', 'Unjustified'),
                                   ('justified', 'Justified'),
                                   ], 'State'),
        'time_table_id': fields.many2one('pedagogy.time_table', 'Time Table'),
        'enrollment_id': fields.many2one('pedagogy.enrollment', 'Enrollment', ondelete='cascade', required=True),
        'student_id': fields.related('enrollment_id', 'student_id', type='many2one', relation='res.partner', store=True,
                                     string='Student'),
        'history_ids': fields.one2many('pedagogy.student.attendance.history', 'attendance_id', 'History'),
        'class_year_id': fields.related('enrollment_id', 'class_year_id', type='many2one',
                                        relation='pedagogy.class.year', string='Class/Year'),
        'class_id': fields.related('class_year_id', 'class_id', type='many2one', relation='pedagogy.class',
                                   string='Class'),
        'year_id': fields.related('class_year_id', 'year_id', type='many2one', relation='pedagogy.school.year',
                                  string='Year'),
        'date_start': fields.related('time_table_id', 'date_from', type='datetime', relation='pedagogy.time_table',
                                     string='Date Start'),
        'date_end': fields.related('time_table_id', 'date_to', type='datetime', relation='pedagogy.time_table',
                                   string='Date End'),
        'class_discipline_teacher_id': fields.related('time_table_id', 'class_discipline_teacher_id', type='many2one',
                                                      relation='pedagogy.class.discipline.teacher', string='Class'),
    }

    _defaults = {
        'state': 'unknown',
    }

    _sql_constraints = [
        ('time_table_enrollment_uniq', 'unique (time_table_id,enrollment_id)', 'The enrollment must unique!'),
    ]


class pedagogy_student_attendance_history(osv.osv):
    _name = 'pedagogy.student.attendance.history'
    _description = 'Student Attendance History'

    _columns = {
        'attendance_id': fields.many2one('pedagogy.student.attendance', 'Attendance', ondelete='cascade',
                                         required=True),
        'user_id': fields.many2one('res.users', 'User', ondelete='cascade', required=True),
        'student_id': fields.many2one('res.partner', 'Student', ondelete='cascade', required=True),
        'time_table_id': fields.related('attendance_id', 'time_table_id', type='many2one',
                                        relation='pedagogy.time_table', string='Time Table'),
        'date': fields.datetime('Date', required=True),
        'change': fields.char('Change', size=128, required=True),
        'justification': fields.text('Justification', size=128),
    }

    _order = 'date desc'
