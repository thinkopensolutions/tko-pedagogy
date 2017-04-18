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


class pedagogy_evaluation_qualitative(osv.osv):
    _name = 'pedagogy.evaluation.qualitative'

    _columns = {'name': fields.char('Name', size=128, required=True, translate=True),
                'note_from': fields.integer('From [>=]', required=True),
                'note_to': fields.integer('To [<]', required=True),
                'observations': fields.text('Observations', translate=True)
                }

    _sql_constraints = [
        ('from_lower_than_to',
         'CHECK (pedagogy_evaluation_qualitative.note_from < pedagogy_evaluation_qualitative.note_to)',
         'From must be lower than To!')
    ]


class qualitative_evaluation_student(osv.osv):
    _name = 'pedagogy.evaluation.student'
    _inherit = 'pedagogy.evaluation.student'

    def _get_qualitative(self, cr, uid, ids, field_name, arg, context):
        res = {}
        qualitative_obj = self.pool.get('pedagogy.evaluation.qualitative')

        def _get_qualitative(obj, note):
            if note > 0:
                qualitative_note_id = obj.search(cr, uid, [('note_from', '<=', note), ('note_to', '>', note)])
                if qualitative_note_id:
                    note = obj.read(cr, uid, qualitative_note_id, ['name'])[0]['name']
                else:
                    note = 'undefined'
            else:
                note = '-'
            return note

        for note in self.browse(cr, uid, ids):
            res[note.id] = {
                'arithmetic_qualitative': _get_qualitative(qualitative_obj, note.arithmetic_classification),
                'teacher_qualitative': _get_qualitative(qualitative_obj, note.teacher_classification),
                'final_qualitative': _get_qualitative(qualitative_obj, note.final_classification)
            }
        return res

    _columns = {
        'arithmetic_qualitative': fields.function(_get_qualitative, method=True, multi='all', type='char',
                                                  string='Arithmetic Qualitative'),
        'teacher_qualitative': fields.function(_get_qualitative, method=True, multi='all', type='char',
                                               string='Teacher Qualitative'),
        'final_qualitative': fields.function(_get_qualitative, method=True, multi='all', type='char',
                                             string='Final Qualitative'),
    }
