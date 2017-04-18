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


class enrollments_grouped_by_year_class_type(osv.osv):
    _name = 'enrollments.grouped.by.year.class.type'
    _inherit = 'enrollments.grouped.by.year.class'
    _auto = False

    _columns = {
        'type': fields.char('Type', size=64, required=True),
    }

    def init(self, cr):
        tools.sql.drop_view_if_exists(cr, 'enrollments_grouped_by_year_class_type')
        cr.execute('''
        CREATE or REPLACE view enrollments_grouped_by_year_class_type as (
            SELECT                
                    min(e.id) as id,   
                    COUNT(e.id) as total_enrollments,
                    y.name as year,
                    c.name as class,
                    t.name as type
                FROM
                    pedagogy_enrollment e,
                    pedagogy_class_year cy,
                    pedagogy_school_year y,
                    pedagogy_class c,
                    pedagogy_class_type t
                WHERE
                        e.state = 'enrolled' AND
                        e.class_year_id = cy.id AND
                        cy.class_id = c.id AND
                        cy.year_id = y.id AND
                        c.class_type_id = t.id
                GROUP BY
                    cy.year_id, cy.class_id, y.name, c.name, t.name
                    )
        ''')
