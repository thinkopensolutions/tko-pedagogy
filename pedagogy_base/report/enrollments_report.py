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
from openerp.osv import fields, osv


class enrollments_report(osv.osv):
    _name = 'pedagogy.enrollments.report'
    _description = 'Enrollments Report'
    _auto = False

    _columns = {
        'number': fields.char('Number', size=64, readonly=True),
        'student_id': fields.many2one('res.partner', 'Student', domain=[('is_student', '=', True)], readonly=True),
        'year_id': fields.many2one('pedagogy.school.year', 'Year', readonly=True),
        'area_id': fields.many2one('pedagogy.group.area', 'Area', readonly=True),
        'group_id': fields.many2one('pedagogy.group', 'Group', readonly=True),
        'class_id': fields.many2one('pedagogy.class', 'Class', readonly=True),
        'state': fields.selection([('new', 'New'),
                                   ('pre_enrolled', 'Pre-Enrolled'),
                                   ('enrolled', 'Enrolled'),
                                   ('canceled', 'Canceled'),
                                   ('suspended', 'Suspended')], 'State', readonly=True),
        'date_start': fields.date('date_start'),
    }
    _order = 'number desc'

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
