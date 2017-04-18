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

from datetime import date, datetime

from osv import fields
from osv import osv


class pedagogy_student(osv.osv):
    _name = 'res.partner'
    _inherit = 'res.partner'

    def name_get(self, cr, user, ids, context={}):
        res = []
        if not 'default_is_student' in context:
            res = super(pedagogy_student, self).name_get(cr, user, ids, context=context)
        else:
            for record in self.browse(cr, user, ids, context=context):
                res.append((record.id, record.name))
        return res

    def _age(self, birth_date):
        now = date.today()
        age_date = datetime.strptime(birth_date, '%Y-%m-%d').date()
        age = now.year - age_date.year - (
        0 if (now.month > age_date.month or (now.month == age_date.month and now.day >= age_date.day)) else 1)
        return age

    def _calculate_age(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for student in self.browse(cr, uid, ids):
            if student.birth_date:
                res[student.id] = self._age(student.birth_date)
            else:
                res[student.id] = 0
        return res

    def create(self, cr, uid, vals, context=None):
        if 'is_student' in vals and vals['is_student']:
            vals.update({'student_number': self.pool.get('ir.sequence').get(cr, uid, 'pedagogy.students.sequence')})
        return super(pedagogy_student, self).create(cr, uid, vals, context)

    def onchange_address_partner_id(self, cr, uid, id, address_partner_id=False):
        result = {}
        if address_partner_id:
            partner = self.pool.get('res.partner').read(cr, uid, [address_partner_id],
                                                        ['street', 'street2', 'city', 'state_id', 'zip', 'country_id'])
            result = {'value': {'country_id': partner[0]['country_id'],
                                'state_id': partner[0]['state_id'],
                                'city': partner[0]['city'],
                                'street': partner[0]['street'],
                                'street2': partner[0]['street2'],
                                'zip': partner[0]['zip'],
                                }}
        return result

    def onchange_birth_date(self, cr, uid, id, birth_date=False):
        result = {}
        if birth_date:
            age = self._age(birth_date)
            result = {'value': {'age': age}}
        return result

    def _latest_enrollment(self, cr, uid, ids, context=None):
        res = {}

        users = ''
        for id in ids:
            res[id] = False;
            users = users + str(id) + ','

        query = 'SELECT DISTINCT ON (res_partner.id) \
                            res_partner.id, \
                            pedagogy_enrollment.id, \
                            pedagogy_school_year.coordinator_id, \
                            pedagogy_group_area.coordinator_id, \
                            pedagogy_class_year.coordinator_id \
                        FROM \
                            res_partner \
                        INNER JOIN pedagogy_enrollment ON (res_partner.id = pedagogy_enrollment.student_id) \
                        INNER JOIN pedagogy_class_year ON (pedagogy_enrollment.class_year_id = pedagogy_class_year.id) \
                        INNER JOIN pedagogy_school_year ON (pedagogy_class_year.year_id = pedagogy_school_year.id) \
                        INNER JOIN pedagogy_class ON (pedagogy_class_year.class_id = pedagogy_class.id) \
                        INNER JOIN pedagogy_group ON (pedagogy_class.group_id = pedagogy_group.id) \
                        INNER JOIN pedagogy_group_area ON (pedagogy_group.group_area_id = pedagogy_group_area.id) \
                        WHERE \
                            res_partner.id in ({0}) \
                            AND pedagogy_enrollment.state in {1} \
                        ORDER BY \
                            res_partner.id, pedagogy_enrollment.number desc'.format(users[:-1],
                                                                                    ('enrolled', 'suspended'))

        cr.execute(query)
        result = cr.fetchall()
        for row in result:
            #            res[row[0]] = {'enrollment_id': row[1],
            #                           'year_coordinator_id': row[2],
            #                           'group_coordinator_id': row[3],
            #                           'class_coordinator_id': row[4]
            #                           }
            res[row[0]] = row[1]

        return res

    def _get_latest_enrollment(self, cr, uid, ids, field_name, args, context=None):
        return self._latest_enrollment(cr, uid, ids, context)

    _columns = {
        'is_student': fields.boolean('Is Student?'),
        'student_number': fields.integer('Number', readonly=True),
        'birth_date': fields.date('Birth Date'),
        'age': fields.function(_calculate_age, method=True, type='integer', string='Age'),
        'gender': fields.selection([('male', 'Male'), ('female', 'Female')], string='Gender'),
        'tutor_id': fields.many2one('res.partner', 'Tutor',
                                    domain=[('is_company', '=', False), ('is_student', '=', False)]),
        'address_partner_id': fields.many2one('res.partner', 'Address From'),
        'enrollment_ids': fields.one2many('pedagogy.enrollment', 'student_id', 'Enrollments'),
        'enrollment_id': fields.function(_get_latest_enrollment, string='Current Enrollment', method=True,
                                         type='many2one', relation='pedagogy.enrollment',
                                         help='Latest enrollment of the student'),
        'year_coordinator_id': fields.related('enrollment_id', 'class_year_id', 'year_id', 'coordinator_id',
                                              type='many2one', relation='hr.employee', string='Year Coordinator',
                                              readonly=True),
        'group_coordinator_id': fields.related('enrollment_id', 'class_year_id', 'coordinator_id', type='many2one',
                                               relation='hr.employee', string='Group Area Coordinator', readonly=True),
        'class_coordinator_id': fields.related('enrollment_id', 'class_year_id', 'class_id', 'group_id',
                                               'group_area_id', 'coordinator_id', type='many2one',
                                               relation='hr.employee', string='Class Coordinator', readonly=True),
        #        'enrollment_id':fields.function(_get_latest_enrollment, string='Current Enrollment', method=True, multi='latest_enrollment', type='many2one', relation='pedagogy.enrollment', help='Latest enrollment of the student'),
        #        'year_coordinator_id':fields.function(get_latest_enrollment, string='Year Coordinator', method=True, multi='latest_enrollment', type='many2one', relation='hr.employee', help='Schyool year coordinator'),
        #        'group_coordinator_id':fields.function(get_latest_enrollment, string='Group Coordinator', method=True, multi='latest_enrollment', type='many2one', relation='hr.employee', help='Group coordinator'),
        #        'class_coordinator_id':fields.function(get_latest_enrollment, string='Class Coordinator', method=True, multi='latest_enrollment', type='many2one', relation='hr.employee', help='Class coordinator'),
    }

    _order = 'student_number desc'
