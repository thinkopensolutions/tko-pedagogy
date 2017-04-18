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

from osv import osv, fields


class bmi(osv.osv):
    _name = 'pedagogy.medical.bmi'

    def _calculate(self, height, weight):
        if weight:
            bmi = int(weight / ((height / 100.0) ** 2))
        else:
            bmi = 0
        return bmi

    def _calculate_bmi(self, cr, uid, ids, field_name, arg, context={}):
        res = {}
        for bmi in self.browse(cr, uid, ids):
            res[bmi.id] = self._calculate(bmi.height, bmi.weight)
        return res

    def _get_qualitative(self, cr, uid, ids, field_name, arg, context):
        res = {}
        qualitative_pool = self.pool.get('pedagogy.medical.bmi.qualitative')
        bmis = self._calculate_bmi(cr, uid, ids, field_name, arg, context)
        for bmi in bmis:
            res[bmi] = qualitative_pool.search(cr, uid, [('bmi_from', '<=', bmis[bmi]), ('bmi_to', '>', bmis[bmi])])
            if res[bmi]:
                res[bmi] = qualitative_pool.read(cr, uid, res[bmi], ['name'])[0]['name']
            else:
                res[bmi] = 'undefined'
        return res

    def onchange_data(self, cr, uid, ids, height, weight, context=None):
        if height and weight:
            bmi_value = self._calculate(height, weight)
            qualitative_pool = self.pool.get('pedagogy.medical.bmi.qualitative')
            qualitative = qualitative_pool.search(cr, uid, [('bmi_from', '<=', bmi_value), ('bmi_to', '>', bmi_value)])
            qualitative = qualitative_pool.read(cr, uid, qualitative, ['name'])[0]['name']
            return {'value': {'bmi': bmi_value,
                              'bmi_qualitative': qualitative}}
        else:
            return {}

    _columns = {
        'student_id': fields.many2one('res.partner', 'Student', domain=[('is_student', '=', True)], required=True),
        'user_id': fields.many2one('res.users', 'User', required=True),
        'measure_date': fields.datetime('Measure Date', required=True),
        'height': fields.integer('Height (cm)', required=True),
        'weight': fields.integer('Weight (kg)', required=True),
        'bmi': fields.function(_calculate_bmi, method=True, type='integer', string='BMI'),
        'bmi_qualitative': fields.function(_get_qualitative, method=True, type='char', size=128,
                                           string='BMI Qualitative')
        }

    _defaults = {'measure_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                 'user_id': lambda self, cr, uid, context=None: uid,}

    _order = 'measure_date desc'


class bmi_qualitative(osv.osv):
    _name = 'pedagogy.medical.bmi.qualitative'
    _columns = {'name': fields.char('Name', size=128, required=True, translate=True),
                'bmi_from': fields.integer('From [>=kg]', required=True),
                'bmi_to': fields.integer('To [<kg]', required=True),
                'observations': fields.text('Observations', translate=True)
                }
    _sql_constraints = [
        ('from_lower_than_to',
         'CHECK (pedagogy_medical_bmi_qualitative.bmi_from < pedagogy_medical_bmi_qualitative.bmi_to)',
         'From must be lower than To!')
    ]
