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

from osv import fields, osv


class students_tutor_list(osv.osv_memory):
    _name = 'students.tutor.list'
    _description = 'Students Tutor List'

    _columns = {
        'pedagogy_school_year_id': fields.many2one('pedagogy.school.year', 'School Year', required=True),
        'pedagogy_class_ids': fields.many2many('pedagogy.class', string='Classes'),
    }

    def _build_contexts(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        result = {}
        result['pedagogy_school_year_id'] = data['form']['pedagogy_school_year_id']
        result['pedagogy_class_ids'] = 'pedagogy_class_ids' in data['form'] and data['form'][
            'pedagogy_class_ids'] or False
        return result

    def _print_report(self, cr, uid, ids, data, context=None):
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'student.tutor.list',
            'datas': data,
        }

    def check_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = {}
        data['ids'] = context.get('active_ids', [])
        data['model'] = context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(cr, uid, ids, ['pedagogy_school_year_id', 'pedagogy_class_ids'])[0]
        used_context = self._build_contexts(cr, uid, ids, data, context=context)
        data['form']['used_context'] = used_context
        return self._print_report(cr, uid, ids, data, context=context)
