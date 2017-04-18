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


class pedagogy_school_year(osv.osv):
    _name = 'pedagogy.school.year'
    _inherit = 'pedagogy.school.year'
    _columns = {'project_id': fields.many2one('project.project', 'Related Project')}


class pedagogy_group(osv.osv):
    _name = 'pedagogy.group'
    _inherit = 'pedagogy.group'
    _columns = {'project_id': fields.many2one('project.project', 'Related Project')}


class pedagogy_group_area(osv.osv):
    _name = 'pedagogy.group.area'
    _inherit = 'pedagogy.group.area'
    _columns = {'project_id': fields.many2one('project.project', 'Related Project')}


class pedagogy_class_year(osv.osv):
    _name = 'pedagogy.class.year'
    _inherit = 'pedagogy.class.year'
    _columns = {'project_id': fields.many2one('project.project', 'Related Project')}


class pedagogy_discipline(osv.osv):
    _name = 'pedagogy.discipline'
    _inherit = 'pedagogy.discipline'
    _columns = {'project_id': fields.many2one('project.project', 'Related Project')}


class class_year_discipline(osv.osv):
    _name = 'pedagogy.class.year.discipline'
    _columns = {'name': fields.related('discipline_id', 'name', type='char', string='Name'),
                'class_year_id': fields.many2one('pedagogy.class.year', 'Class/Year', required=True),
                'discipline_id': fields.many2one('pedagogy.discipline', 'Discipline', required=True),
                'project_id': fields.many2one('project.project', 'Related Project', required=True)}
    _sql_constraints = [
        ('pair_uniq', 'unique(class_year_id, discipline_id)', 'Must be unique!'),
    ]


class group_area_year(osv.osv):
    _name = 'pedagogy.group.area.year'
    _columns = {'name': fields.related('group_area_id', 'name', type='char', string='Name'),
                'group_area_id': fields.many2one('pedagogy.group.area', 'Area', required=True),
                'year_id': fields.many2one('pedagogy.school.year', 'Year', required=True),
                'project_id': fields.many2one('project.project', 'Related Project')
                }
    _sql_constraints = [
        ('pair_uniq', 'unique(group_area_id, year_id)', 'Must be unique!'),
    ]


class group_year(osv.osv):
    _name = 'pedagogy.group.year'
    _columns = {'name': fields.related('group_id', 'name', type='char', string='Name'),
                'group_id': fields.many2one('pedagogy.group', 'Group', required=True),
                'year_id': fields.many2one('pedagogy.school.year', 'Year', required=True),
                'project_id': fields.many2one('project.project', 'Related Project')
                }
    _sql_constraints = [
        ('pair_uniq', 'unique(group_id, year_id)', 'Must be unique!'),
    ]
