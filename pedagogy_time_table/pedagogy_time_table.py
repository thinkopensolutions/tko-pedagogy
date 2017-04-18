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


class pedagogy_time_table(osv.osv):
    _name = 'pedagogy.time_table'
    _description = 'Pedagogy Time Tables'

    def _is_coordinator(self, cr, uid):
        user_pool = self.pool.get('res.users')
        [user] = user_pool.browse(cr, uid, [uid])
        if user.login == u'admin':
            return True
        for group in user.groups_id:
            if group.name == u'Pedagogy / Coordinator':
                return True
        return False

    def _is_owner(self, cr, uid, ids, field_name, arg, context=None):
        if self._is_coordinator(cr, uid):
            return dict(map(lambda id: (id, True), ids))
        res = {}
        for time_table in self.browse(cr, uid, ids, context=context):
            res[time_table.id] = (time_table.teacher_id.user_id.id == uid)
        return res

    def _find_project(self, cr, uid, ids, field_name, arg, context=None):
        pool = self.pool.get('pedagogy.class.year.discipline')
        res = {}
        for TT in self.browse(cr, uid, ids, context=context):
            try:
                query = [('class_year_id', '=', TT.class_year_id.id),
                         ('discipline_id', '=', TT.discipline_id.id)]
                ids = pool.search(cr, uid, query, context=context)
                [obj] = pool.browse(cr, uid, ids, context=context)
                res[TT.id] = obj.project_id.id
            except ValueError:
                pass
        return res

    _columns = {
        'owner': fields.function(_is_owner, method=True, type='boolean'),
        'class_year_id': fields.related('class_discipline_teacher_id', 'class_year_id', type='many2one',
                                        relation='pedagogy.class.year', string='Class', readonly=True),
        'teacher_id': fields.related('class_discipline_teacher_id', 'teacher_id', type='many2one',
                                     relation='hr.employee', string='Teacher', readonly=True),
        'name': fields.related('class_discipline_teacher_id', 'name', type='char', string='Name', readonly=True,
                               help='Read only field, time table entry name.'),
        'activity_ids': fields.one2many('pedagogy.activity', 'time_table_id', 'Activities', ondelete='cascade'),
        'date_from': fields.datetime('Date From', required=True, select=1),
        'date_to': fields.datetime('Date To', required=True, select=2),
        'class_discipline_teacher_id': fields.many2one('pedagogy.class.discipline.teacher', 'Class', select=1,
                                                       required=True),
        'discipline_id': fields.related('class_discipline_teacher_id', 'discipline_id', type='many2one',
                                        relation='pedagogy.discipline', string='Discipline', readonly=True),
        'project_id': fields.function(_find_project, method=True, type='many2one', relation='project.project',
                                      string='Project'),
        'task_ids': fields.many2many('project.task', 'pedagogy_content_task_rel', 'time_table_ids', 'task_ids',
                                     'Tasks'),
        'timesheet_ids': fields.one2many('project.task.work', 'time_table_id', 'Timesheet'),
    }

    _order = 'date_from'

    _defaults = {
        'owner': True,
    }


class pedagogy_time_table_timesheets(osv.osv):
    _name = 'project.task.work'
    _inherit = 'project.task.work'

    def _get_available_tasks(self, cr, uid, context):  # 'task_ids': [[6, False, [64, 65]]],
        if 'task_ids' in context:
            [(code, update, task_ids)] = context['task_ids']
            return task_ids
        else:
            return []

    _columns = {
        'available_tasks': fields.function(lambda *a: {}, type='one2many', relation='project.task'),
        'time_table_id': fields.many2one('pedagogy.time_table', 'Time Table'),
    }
    _defaults = {
        'available_tasks': _get_available_tasks,
    }
