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

import tools
from osv import fields
from osv import osv
from tools.translate import _


class pedagogy_enrollment(osv.osv):
    _name = 'pedagogy.enrollment'
    _description = 'Enrollments'

    _state_dict_tansl = {
        'new': _('New'),
        'pre_enrolled': _('Pre-enrolled'),
        'enrolled': _('Enrolled'),
        'canceled': _('Canceled'),
        'suspended': _('Suspended'),
    }

    def create(self, cr, uid, vals, context=None):
        if context and 'class_year_copy' in context:
            return None
        new_id = super(pedagogy_enrollment, self).create(cr, uid, vals, context)
        # create the first history line
        self.pool.get('pedagogy.enrollment.history').create(cr, uid, {'enrollment_id': new_id,
                                                                      'user_id': uid,
                                                                      'date': datetime.now().strftime(
                                                                          '%Y-%m-%d %H:%M:%S'),
                                                                      'change': self._state_dict_tansl['new']}
                                                            )
        return new_id

    def unlink(self, cr, uid, ids, context=None):
        stat = self.read(cr, uid, ids, ['state'], context=context)
        unlink_ids = []
        for t in stat:
            if t['state'] in ('new'):
                unlink_ids.append(t['id'])
            else:
                raise osv.except_osv(_('Invalid Action!'), _('You can\'t delete an enrollment with this state.'))
        osv.osv.unlink(self, cr, uid, unlink_ids, context=context)
        return True

    def copy_data(self, cr, uid, id, default=None, context=None):
        if context and 'source' in context and context['source'] == 'wizard':
            return
        parent = super(pedagogy_enrollment, self)
        return parent.copy_data(cr, uid, id, default, context=context)

    def set_sequence(self, cr, uid, ids, *args):
        for obj in self.browse(cr, uid, ids):
            if not obj.number:
                self.write(cr, uid, obj.id, {
                    'number': self.pool.get('ir.sequence').get(cr, uid, 'pedagogy.enrollment.sequence')} or False)
        return True

    def write_history(self, cr, uid, ids, *args):
        for obj in self.browse(cr, uid, ids):
            self.pool.get('pedagogy.enrollment.history').create(cr, uid, {'enrollment_id': obj.id,
                                                                          'user_id': uid,
                                                                          'date': datetime.now().strftime(
                                                                              '%Y-%m-%d %H:%M:%S'),
                                                                          'change': self._state_dict_tansl[obj.state]}
                                                                )
        return True

    def _get_name(self, cr, uid, ids, fn, args, context=None):
        res = {}
        for rec in self.browse(cr, uid, ids):
            name = u'{0} [{1}]'
            res[rec.id] = name.format(rec.class_year_id.name,
                                      rec.number)
        return res

    def _enrollment_search(self, cr, uid, obj, name, args, context):
        res = []
        query = 'SELECT pedagogy_enrollment.id \
                        FROM \
                            pedagogy_enrollment \
                        INNER JOIN \
                            pedagogy_class_year \
                        ON \
                            pedagogy_enrollment.class_year_id = pedagogy_class_year.id \
                        WHERE \
                            (pedagogy_class_year.name || \' [\' || pedagogy_enrollment.number || \']\') ilike %s'
        cr.execute(query, ('%' + args[0][2] + '%',))
        res = [('id', 'in', cr.fetchall())]
        return res

    _columns = {
        'name': fields.function(_get_name, fnct_search=_enrollment_search, string='Name', method=True, type='char',
                                size=128),
        'number': fields.char('Number', size=64),
        'class_year_id': fields.many2one('pedagogy.class.year', 'Class/Year', required=True),
        'class_id': fields.related('class_year_id', 'class_id', type='many2one', relation='pedagogy.class',
                                   string='Class'),
        'group_id': fields.related('class_id', 'group_id', type='many2one', relation='pedagogy.group', readonly=True),
        'group_area_id': fields.related('group_id', 'group_area_id', type='many2one', relation='pedagogy.group.area',
                                        string='Area', readonly=True),
        'year_id': fields.related('class_year_id', 'year_id', type='many2one', relation='pedagogy.school.year',
                                  string='Year'),
        'student_id': fields.many2one('res.partner', 'Student', domain=[('is_student', '=', True)], ondelete='cascade',
                                      required=True),
        'state': fields.selection([('new', 'New'),
                                   ('pre_enrolled', 'Pre-Enrolled'),
                                   ('enrolled', 'Enrolled'),
                                   ('canceled', 'Canceled'),
                                   ('suspended', 'Suspended')], 'State', required=True, readonly=True),
        'observations': fields.text('Observations', size=128),
        'history_ids': fields.one2many('pedagogy.enrollment.history', 'enrollment_id', 'History'),
    }

    _sql_constraints = [
        ('class_year_student_unique', 'unique (class_year_id,student_id)',
         'The student is already enrolled in that Class/Year!')
    ]

    _defaults = {
        'state': 'new',
        # to prevent from appearing a false in from this field in view if field empty
        'observations': ' ',
    }

    _order = 'number desc'


class pedagogy_enrollment_history(osv.osv):
    _name = 'pedagogy.enrollment.history'
    _description = 'Enrollment History'

    _columns = {
        'enrollment_id': fields.many2one('pedagogy.enrollment', 'Enrollment', ondelete='cascade', required=True),
        'user_id': fields.many2one('res.users', 'User', ondelete='cascade', required=True),
        'date': fields.datetime('Date', required=True),
        'change': fields.char('Change', size=128, required=True),
    }

    _order = 'date desc'


class enrollments_by_school_year(osv.osv):
    _name = 'enrollments.by.school.year'
    _description = 'Enrollments By School Year'
    _auto = False

    _columns = {
        'year_id': fields.char('Year', size=64, readonly=True),
        'total_enrollments': fields.integer('Total Enrollments', readonly=True),
    }

    def init(self, cr):
        tools.sql.drop_view_if_exists(cr, 'enrollments_by_school_year')
        cr.execute('''
            CREATE or REPLACE view enrollments_by_school_year as (
                SELECT
                    min(e.id) as id,
                    COUNT(e.id) as total_enrollments,
                    y.name as year_id
                FROM
                    pedagogy_enrollment as e,
                    pedagogy_class_year cy,
                    pedagogy_school_year as y
                WHERE
                    e.state = 'enrolled'
                    AND e.class_year_id = cy.id
                    AND cy.year_id = y.id
                GROUP BY
                    y.name
            )
        ''')


class enrollments_grouped_by_year_class(osv.osv):
    _name = 'enrollments.grouped.by.year.class'
    _description = 'Enrollments Grouped By Year and Class'
    _auto = False

    _columns = {
        'year_id': fields.char('Year', size=64, required=True),
        'class_id': fields.char('Class', size=64, required=True),
        'total_enrollments': fields.integer('Total enrollments', readonly=True),
    }

    def init(self, cr):
        tools.sql.drop_view_if_exists(cr, 'enrollments_grouped_by_year_class')
        cr.execute('''
        CREATE or REPLACE view enrollments_grouped_by_year_class as (
            SELECT
                min(e.id) as id,
                COUNT(e.id) as total_enrollments,
                y.name as year_id,
                c.name as class_id
            FROM
                pedagogy_enrollment e,
                pedagogy_class_year cy,
                pedagogy_school_year y,
                pedagogy_class c
            WHERE
                e.state = 'enrolled' AND
                e.class_year_id = cy.id AND
                cy.class_id = c.id AND
                cy.year_id = y.id
            GROUP BY
                cy.class_id, y.name, c.name
                )
        ''')
