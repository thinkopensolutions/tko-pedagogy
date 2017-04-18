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


class birthday(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(birthday, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'classes': self.classes,
            'students': self.students,
        })

    # didn't set context to enable all classes in report overriding student selection
    # def set_context(self, objects, data, ids, report_type=None):
    def classes(self):
        res = []
        pedagogy_class = self.pool.get('pedagogy.class')
        ids = pedagogy_class.search(self.cr, self.uid, [])
        classes = pedagogy_class.browse(self.cr, self.uid, ids)
        for class_ in classes:
            for class_year in class_.class_years:
                if class_year.enrollments:
                    res.append(class_)
        return res

    def students(self, classes):
        res = []
        res_partner_obj = self.pool.get('res.partner')
        for class_year in classes.class_years:
            for enrollment in class_year.enrollments:
                res.append(enrollment.student.id)
        sorted_student_ids = res_partner_obj.search(self.cr, self.uid, [('id', 'in', res)], order='birth_date asc')
        return res_partner_obj.browse(self.cr, self.uid, sorted_student_ids)


report_sxw.report_sxw(
    'report.birthday',
    'res.partner',
    'pedagogy_base/report/birthday.rml',
    parser=birthday
)
