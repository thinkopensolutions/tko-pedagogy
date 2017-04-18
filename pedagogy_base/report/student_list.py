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

import time

from report import report_sxw


class classes(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(classes, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_school_year': self.get_school_year,
        })

    def get_school_year(self, data):
        res = ''
        if data['form']['pedagogy_school_year_id']:
            res = 'Ano Escolar: ' + data['form']['pedagogy_school_year_id'][1]
        return res

    def set_context(self, objects, data, ids, report_type=None):
        new_ids = ids
        pedagogy_enrollment_obj = self.pool.get('pedagogy.enrollment')
        pedagogy_school_year_id = data['form']['pedagogy_school_year_id']
        pedagogy_class_ids = []
        query_params = [('state', '=', 'enrolled')]
        if data['form']['pedagogy_class_ids']:
            query_params = [
                ('state', '=', 'enrolled'),
                ('class_id', 'in', data['form']['pedagogy_class_ids'])]
        pedagogy_enrollment_ids = pedagogy_enrollment_obj.search(self.cr, self.uid, query_params, order='class_year_id')
        pedagogy_enrollments = pedagogy_enrollment_obj.browse(self.cr, self.uid, pedagogy_enrollment_ids)
        objects = pedagogy_enrollments
        if pedagogy_school_year_id:
            objects = [x for x in pedagogy_enrollments if x.class_year_id.year.id == pedagogy_school_year_id[0]]
        return super(classes, self).set_context(objects, data, new_ids, report_type=report_type)


report_sxw.report_sxw(
    'report.student.list',
    'pedagogy.enrollment',
    'pedagogy_base/report/student_list.rml',
    parser=classes
)

report_sxw.report_sxw(
    'report.student.tutor.list',
    'pedagogy.enrollment',
    'pedagogy_base/report/student_tutor_list.rml',
    parser=classes
)
