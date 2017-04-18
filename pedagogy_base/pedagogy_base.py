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

from datetime import datetime

from openerp.osv import osv, fields


class pedagogy_group(osv.osv):
    _name = 'pedagogy.group'
    _description = 'Pedagogy Groups'

    _columns = {
        'name': fields.char('Group Name', size=128, required=True, help='This is the organization of students in commons groups regarding content.\n\
Its a group definition, later you can define several classes of this group.\n\
(ex:. 3 Years old, Class 1, Class 8)'),
        'group_area_id': fields.many2one('pedagogy.group.area', 'Group Area', required=True),
        'class_ids': fields.one2many('pedagogy.class', 'group_id', 'Grouped classes'),
    }


class pedagogy_group_area(osv.osv):
    _name = 'pedagogy.group.area'
    _description = 'Pedagogy Group Areas'

    _columns = {
        'name': fields.char('Group Area Name', size=128, required=True,
                            help='This is the organization of common groups in areas.\n\n(ex:. preschool, classes 1-9, high school)'),
        'group_ids': fields.one2many('pedagogy.group', 'group_area_id', 'Groups'),
        'coordinator_id': fields.many2one('hr.employee', 'Coordinator'),
    }
    _order = 'name'


class pedagogy_school_year(osv.osv):
    _name = 'pedagogy.school.year'
    _description = 'Pedagogy School Years'

    def _get_this_year(self, cr, uid, ids, field_name, arg, context):
        res = {}
        # Look for actual year
        actual_year_start = datetime.now().strftime('%Y-%m-%d')
        actual_year_end = actual_year_start
        for year in self.browse(cr, uid, ids, context):
            res[year.id] = 'future'
            if year.date_start <= datetime.now().strftime('%Y-%m-%d'):
                res[year.id] = 'old'
                if year.date_end >= datetime.now().strftime('%Y-%m-%d'):
                    res[year.id] = 'this'
                    actual_year_start = year.date_start
                    actual_year_end = year.date_end
        # Look for next one
        one_year = self.search(cr, uid, [('date_start', '>', actual_year_end)], order='date_start asc', limit=1,
                               context=context)
        if one_year:
            res[one_year[0]] = 'next'
        # Look for last one
        one_year = self.search(cr, uid, [('date_end', '<', actual_year_start)], order='date_end desc', limit=1,
                               context=context)
        if one_year:
            res[one_year[0]] = 'last'

        return res

    def _search_this_year(self, cr, uid, obj, name, args, context):
        res = []
        date_now = datetime.now().strftime('%Y-%m-%d')
        # there is the option to select this year between the start of this year and the start of next one
        # instead between the start and end of one
        if args[0][2] == 'future':
            years = self.search(cr, uid, [('date_start', '>', date_now)], order='date_start asc', context=context)
            # remove id of next year (first element), kept only the future ones
            # years = years[1:]
        elif args[0][2] == 'next':
            years = self.search(cr, uid, [('date_start', '>', date_now)], order='date_end asc', limit=1,
                                context=context)
        elif args[0][2] == 'this':
            years = self.search(cr, uid, [('date_start', '<=', date_now), ('date_end', '>=', date_now)],
                                order='date_end asc', limit=1, context=context)
        elif args[0][2] == 'last':
            years = self.search(cr, uid, [('date_end', '<', date_now)], order='date_end desc', limit=1, context=context)
        elif args[0][2] == 'old':
            years = self.search(cr, uid, [('date_end', '<', date_now)], order='date_end desc', context=context)
            # remove id of the last (first element), kept only the old ones
            # years = years[1:]
        else:
            years = []

        if years:
            res = [('id', 'in', years)]

        return res

    _columns = {
        'name': fields.char('Name', size=64, help='Something like year_from/year_to (ex:. 2010/2011).', required=True),
        'date_start': fields.date('Start date', required=True),
        'date_end': fields.date('End date', required=True),
        'this_year': fields.function(_get_this_year, fnct_search=_search_this_year, method=True, translate=True,
                                     type='char', string='This Year Is',
                                     help='Last year give the position of a year this, last, future or old'),
        'coordinator_id': fields.many2one('hr.employee', 'Year Coordinator'),
    }

    _order = 'name desc'
