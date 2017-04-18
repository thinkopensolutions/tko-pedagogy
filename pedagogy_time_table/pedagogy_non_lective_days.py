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


class pedagogy_non_lective_days(osv.osv):
    _name = 'pedagogy.non.lective.days'
    _description = 'Pedagogy Non Lective Days'

    _columns = {'name': fields.char('Name', size=64, required=True, select=1),
                'date_start': fields.datetime('Start', required=True, select=1),
                'date_end': fields.datetime('End', required=True, select=1),
                'observations': fields.text('Observations', size=128),
                'school_year_id': fields.many2one('pedagogy.school.year', 'School Year', select=2, required=True),
                'group_area_id': fields.many2one('pedagogy.group.area', 'Group Area'),
                }
