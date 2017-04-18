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

from osv import osv, fields
from tools.translate import _


class pedagogy_class_discipline_teacher(osv.osv):
    _name = 'pedagogy.class.discipline.teacher'

    def _get_name(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for rec in self.browse(cr, uid, ids):
            name = u'{0} / {1} / {2}'
            res[rec.id] = name.format(rec.class_year_id.name,
                                      rec.discipline_id.name,
                                      rec.teacher_id.resource_id.name)
        return res

    def onchange_date_start(self, cr, uid, ids, date_start=False, class_year_id=False, context=None):
        if not date_start and not class_year_id:
            return {}
        class_year_id_obj = self.pool.get('pedagogy.class.year')
        class_year_id = class_year_id_obj.browse(cr, uid, class_year_id)
        if class_year_id:
            class_year_date_start = class_year_id.year_id.date_start
            class_year_date_end = class_year_id.year_id.date_end
            if date_start < class_year_date_start or date_start > class_year_date_end:
                raise osv.except_osv(_('Invalid Date!'), _('The date must be inserted in range of the school year.'))
        return {}

    def onchange_date_end(self, cr, uid, ids, date_end=False, class_year_id=False, context=None):
        if not date_end and not class_year_id:
            return {}
        class_year_id_obj = self.pool.get('pedagogy.class.year')
        class_year_id = class_year_id_obj.browse(cr, uid, class_year_id)
        if class_year_id:
            class_year_date_start = class_year_id.year_id.date_start
            class_year_date_end = class_year_id.year_id.date_end
            if date_end < class_year_date_start or date_end > class_year_date_end:
                raise osv.except_osv(_('Invalid Date!'), _('The date must be inserted in range of the school year.'))
        return {}

    def _verify_dates(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids):
            try:
                assert obj.date_start <= obj.date_end
                assert obj.date_start >= obj.class_year_id.year_id.date_start
                assert obj.date_end <= obj.class_year_id.year_id.date_end
            except AssertionError:
                raise osv.except_osv(_('Error'), _(
                    'The dates are wrong: start date before end or must be in the selected class School Year!'))
        return True

    def onchange_get_dates_from_year(self, cr, uid, ids, class_year_id, date_start, date_end, context=None):
        result = {}
        if class_year_id:
            [class_year_id] = self.pool.get('pedagogy.class.year').browse(cr, uid, [class_year_id])
            result = {'value': {'date_start': class_year_id.date_start,
                                'date_end': class_year_id.date_end}}
        return result

    def _class_discipline_teacher_search(self, cr, uid, obj, name, args, context):
        res = []
        query = 'SELECT pedagogy_class_discipline_teacher.id \
                        FROM \
                            pedagogy_class_discipline_teacher \
                        WHERE \
                            pedagogy_class_discipline_teacher.name ilike %s'
        cr.execute(query, ('%' + args[0][2] + '%',))
        res = [('id', 'in', cr.fetchall())]
        return res

    def _get_cdt_years(self, cr, uid, ids, context=None):
        cdts = []
        classes_years = self.pool.get('pedagogy.class.year').search(cr, uid, [('year_id', 'in', ids)], context=context)
        cdts = self.pool.get('pedagogy.class.discipline.teacher').search(cr, uid,
                                                                         [('class_year_id', 'in', classes_years)],
                                                                         context=context)
        return cdts

    def _get_cdt_classes(self, cr, uid, ids, context=None):
        cdts = []
        classes_years = self.pool.get('pedagogy.class.year').search(cr, uid, [('class_id', 'in', ids)], context=context)
        cdts = self.pool.get('pedagogy.class.discipline.teacher').search(cr, uid,
                                                                         [('class_year_id', 'in', classes_years)],
                                                                         context=context)
        return cdts

    def _get_cdt_classes_years(self, cr, uid, ids, context=None):
        cdts = []
        cdts = self.pool.get('pedagogy.class.discipline.teacher').search(cr, uid, [('class_year_id', 'in', ids)],
                                                                         context=context)
        return cdts

    def _get_cdt_disciplines(self, cr, uid, ids, context=None):
        cdts = []
        cdts = self.pool.get('pedagogy.class.discipline.teacher').search(cr, uid, [('discipline_id', 'in', ids)],
                                                                         context=context)
        return cdts

    def _get_cdt_teachers(self, cr, uid, ids, context=None):
        cdts = []
        teachers = self.pool.get('hr.employee').search(cr, uid, [('resource_id', 'in', ids)], context=context)
        cdts = self.pool.get('pedagogy.class.discipline.teacher').search(cr, uid, [('teacher_id', 'in', teachers)],
                                                                         context=context)
        return cdts

    _columns = {
        'name': fields.function(_get_name, fnct_search=_class_discipline_teacher_search,
                                store={
                                    'pedagogy.class.discipline.teacher': (lambda self, cr, uid, ids, c={}: ids,
                                                                          ['class_year_id', 'discipline_id',
                                                                           'teacher_id'], 10),
                                    'pedagogy.school.year': (_get_cdt_years, ['name'], 30),
                                    'pedagogy.class': (_get_cdt_classes, ['name'], 30),
                                    'pedagogy.class.year': (_get_cdt_classes_years, ['year_id', 'class_id'], 20),
                                    'pedagogy.discipline': (_get_cdt_disciplines, ['name'], 20),
                                    'resource.resource': (_get_cdt_teachers, ['name'], 30),
                                },
                                method=True, type='char', string='Name'),
        'class_year_id': fields.many2one('pedagogy.class.year', 'Class/Year', required=True, ondelete='cascade'),
        'discipline_id': fields.many2one('pedagogy.discipline', 'Discipline', required=True),
        'teacher_id': fields.many2one('hr.employee', 'Teacher', domain=[('is_teacher', '=', True)], required=True),
        'discipline_area_id': fields.related('discipline_id', 'discipline_area_id', type='many2one',
                                             relation='pedagogy.discipline_area', readonly=True, string='Area'),
        'date_start': fields.date('Start date', required=True),
        'date_end': fields.date('End date', required=True),
        'observations': fields.text('Observations'),
    }

    # to prevent from appearing a false in from this field in view if field empty
    _defaults = {'observations': ' '}

    _sql_constraints = [('class_year_discipline_teacher_uniq', 'unique(class_year_id, discipline_id, teacher_id)',
                         'This teacher already teaches this discipline to this class year!'), ]

    _constraints = [
        (_verify_dates, 'Invalid Dates', ['date_start', 'date_end']),
    ]


class class_year(osv.osv):
    _name = 'pedagogy.class.year'
    _inherit = 'pedagogy.class.year'

    _columns = {
        'class_discipline_teacher_ids': fields.one2many('pedagogy.class.discipline.teacher', 'class_year_id', 'CDTs'),
    }
