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

from openerp import _
from openerp.osv import osv, fields


class pedagogy_class(osv.osv):
    _name = 'pedagogy.class'
    _description = 'Pedagogy Classes'
    _columns = {
        'group_id': fields.many2one('pedagogy.group', 'Group', required=True),
        'name': fields.char('Class Name', size=64, required=True),
        'group_area_id': fields.related('group_id', 'group_area_id', type='many2one', relation='pedagogy.group.area',
                                        readonly=True, string='Group Areas',
                                        help='Read only field, this is all the group areas concatenated.'),
        'class_year_ids': fields.one2many('pedagogy.class.year', 'class_id', 'Class Years'),
    }

    _order = 'group_id, name'


class pedagogy_class_year(osv.osv):
    _name = 'pedagogy.class.year'
    _description = 'Class/Year'

    def _get_name(self, cr, uid, ids, field_name, arg, context):
        def _get_res(class_year):
            class_name = class_year.class_id.name
            year_name = class_year.year_id.name
            return (class_year.id, u'{0} {1}'.format(class_name, year_name))

        class_years = self.browse(cr, uid, ids)
        return dict((_get_res(class_year) for class_year in class_years))

    def _get_num_students(self, cr, uid, ids, field_name, arg, context):
        def _get_num(class_year):
            return (class_year.id, len(class_year.enrollment_ids))

        class_years = self.browse(cr, uid, ids)
        return dict((_get_num(class_year) for class_year in class_years))

    def onchange_date_start(self, cr, uid, ids, date_start=False, year_id=False, context=None):
        if not date_start and not year_id:
            return {}
        year_id_obj = self.pool.get('pedagogy.school.year')
        year_id = year_id_obj.browse(cr, uid, year_id)
        if year_id:
            year_date_start = year_id.date_start
            year_date_end = year_id.date_end
            if date_start < year_date_start or date_start > year_date_end:
                raise osv.except_osv(_('Invalid Date!'), _('The date must be inserted in range of the school year.'))
        return {}

    def onchange_date_end(self, cr, uid, ids, date_end=False, year_id=False, context=None):
        if not date_end and not year_id:
            return {}
        year_id_obj = self.pool.get('pedagogy.school.year')
        year_id = year_id_obj.browse(cr, uid, year_id)
        if year_id:
            year_date_start = year_id.date_start
            year_date_end = year_id.date_end
            if date_end < year_date_start or date_end > year_date_end:
                raise osv.except_osv(_('Invalid Date!'), _('The date must be inserted in range of the school year.'))
        return {}

    def _verify_dates(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids):
            try:
                assert obj.date_start <= obj.date_end
                assert obj.date_start >= obj.year_id.date_start
                assert obj.date_end <= obj.year_id.date_end
            except AssertionError:
                raise osv.except_osv(_('Error'), _(
                    'The dates are wrong: verify if start date before end or must be in the selected School Year!'))
        return True

    def _get_occupancy(self, cr, uid, ids, field_name, arg, context):
        def _get_occupancy(class_year):
            if class_year.capacity:
                return (class_year.id, float(class_year.num_students) / float(class_year.capacity) * 100.0)
            else:
                return 0

        class_years = self.browse(cr, uid, ids)
        return dict((_get_occupancy(class_year) for class_year in class_years))

    def onchange_get_dates_from_year(self, cr, uid, ids, year_id, date_start, date_end, context=None):
        result = {}
        if year_id:
            [year_id] = self.pool.get('pedagogy.school.year').browse(cr, uid, [year_id])
            result = {'value': {'date_start': year_id.date_start,
                                'date_end': year_id.date_end}}
        return result

    def _class_year_search(self, cr, uid, obj, name, args, context):
        res = []
        query = 'SELECT pedagogy_class_year.id \
                        FROM \
                            pedagogy_class_year \
                        WHERE \
                            pedagogy_class_year.name ilike %s'
        cr.execute(query, ('%' + args[0][2] + '%',))
        res = [('id', 'in', cr.fetchall())]
        return res

    def _get_class_year_years(self, cr, uid, ids, context=None):
        """
        The self is school.year class, and this function returns the class_years with changed school_years.ids
        """
        return self.pool.get('pedagogy.class.year').search(cr, uid, [('year_id', 'in', ids)], context=context)

    def _get_class_year_classes(self, cr, uid, ids, context=None):
        return self.pool.get('pedagogy.class.year').search(cr, uid, [('class_id', 'in', ids)], context=context)

    _columns = {
        'name': fields.function(_get_name, fnct_search=_class_year_search,
                                store={
                                    'pedagogy.class.year': (
                                    lambda self, cr, uid, ids, c={}: ids, ['year_id', 'class_id'], 10),
                                    'pedagogy.school.year': (_get_class_year_years, ['name'], 10),
                                    'pedagogy.class': (_get_class_year_classes, ['name'], 10),
                                },
                                method=True, type='char', readonly=True, string='Name'),
        'class_id': fields.many2one('pedagogy.class', 'Class', required=True),
        'year_id': fields.many2one('pedagogy.school.year', 'Year', required=True),
        'date_start': fields.date('Start date', required=True),
        'date_end': fields.date('End date', required=True),
        'coordinator_id': fields.many2one('hr.employee', 'Coordinator'),
        'capacity': fields.integer('Capacity', required=True),
        'num_students': fields.function(_get_num_students, method=True, type='integer', string='Students',
                                        help='Number of Students enrolled in this Class and Year'),
        'occupancy': fields.function(_get_occupancy, method=True, type='float', string='Occupancy (%)',
                                     help='Class occupancy'),
        'enrollment_ids': fields.one2many('pedagogy.enrollment', 'class_year_id', 'Enrollments'),
    }

    _order = 'date_start desc, name asc'

    _sql_constraints = [
        ('class_year_unique', 'unique (class_id, year_id)',
         'There can\'t be more than one record with the same class and year!'),
        ('class_capacity', 'check (capacity>0)', 'Capacity must be greater than zero'),
    ]

    _constraints = [
        (_verify_dates, 'Invalid Dates', ['date_start', 'date_end']),
    ]
