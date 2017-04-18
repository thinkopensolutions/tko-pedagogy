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

from openerp.report import report_sxw


class classes(report_sxw.rml_parse):
    _pedagogy_school_year_id = None

    def __init__(self, cr, uid, name, context):
        super(classes, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'classes': self.classes,
            'enrollments': self.enrollments,
            'student_count': self.student_count,
        })

    def set_context(self, objects, data, ids, report_type=None):
        new_ids = ids
        pedagogy_class_obj = self.pool.get('pedagogy.class')
        self._pedagogy_school_year_id = data['form']['pedagogy_school_year_id'][0]
        query_params = []
        if data['form']['pedagogy_class_ids']:
            query_params = [
                ('id', 'in', data['form']['pedagogy_class_ids'])
            ]
        pedagogy_class_ids = pedagogy_class_obj.search(self.cr, self.uid, query_params)
        objects = pedagogy_class_obj.browse(self.cr, self.uid, pedagogy_class_ids)
        return super(classes, self).set_context(objects, data, new_ids, report_type=report_type)

    def classes(self, ids=[]):
        if not ids:
            ids = self.ids
        res = []
        pedagogy_class = self.pool.get('pedagogy.class')
        classes = pedagogy_class.browse(self.cr, self.uid, ids)
        for class_ in classes:
            for class_year in class_.class_years:
                if class_year.enrollments:
                    res.append(class_)
        return res

    def enrollments(self, classes):
        res = []
        res_partner_obj = self.pool.get('res.partner')
        for class_year in classes.class_years:
            for enrollment in class_year.enrollments:
                if enrollment.state == 'enrolled' and enrollment.class_year_id.year.id == self._pedagogy_school_year_id:
                    res.append(enrollment)
        return res

    def student_count(self, classes):
        res = []
        res_partner_obj = self.pool.get('res.partner')
        for class_year in classes.class_years:
            for enrollment in class_year.enrollments:
                if enrollment.state == 'enrolled' and enrollment.class_year_id.year.id == self._pedagogy_school_year_id:
                    res.append(enrollment)
            if len(res) > 0:
                return len(res)
            else:
                return '0'


report_sxw.report_sxw(
    'report.classes',
    'res.partner',
    'pedagogy_base/report/classes.rml',
    parser=classes
)
