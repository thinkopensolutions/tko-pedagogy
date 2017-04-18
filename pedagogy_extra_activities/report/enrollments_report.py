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


class enrollments_report_with_type(osv.osv):
    _name = 'pedagogy.enrollments.report'
    _inherit = 'pedagogy.enrollments.report'
    _description = 'Enrollments Report'
    _auto = False

    _columns = {
        'type': fields.many2one('pedagogy.class.type', 'Class Type', readonly=True),
    }

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'pedagogy_enrollments_report')
        cr.execute('''
            create or replace view pedagogy_enrollments_report as (
            select
                e.id as id,
                e.number as number,
                e.student_id as student,
                cy.year_id as year,
                g.group_area_id as area,
                g.id as group,
                cl.id as class,
                cl.class_type_id as type,
                e.state as state,
                y.date_start as date_start
            from
                pedagogy_enrollment e
                left join pedagogy_class_year cy on (e.class_year_id = cy.id)
                left join pedagogy_class cl on (cy.class_id = cl.id)
                left join pedagogy_group g on (cl.group_id = g.id)
                left join pedagogy_school_year y on (cy.year_id = y.id)
            )
        ''')
