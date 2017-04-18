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


class pedagogy_kinship_type(osv.osv):
    _name = 'pedagogy.kinship.type'
    _columns = {
        'name': fields.char(_('Name'), size=128, select=True, required=True, translate=True),
    }


class pedagogy_kinship(osv.osv):
    _name = 'pedagogy.kinship'
    _description = _('Family')

    _columns = {'student_id': fields.many2one('res.partner', 'Student', required=True, ondelete='cascade'),
                'person_id': fields.many2one('res.partner', 'Person',
                                             domain=[('is_company', '=', False), ('is_student', '=', False)],
                                             required=True, ondelete='cascade'),
                'type_id': fields.many2one('pedagogy.kinship.type', 'Type', required=True),
                'note': fields.char(_('Observations'), size=128, help=_('Observation Help String')),
                }


class student_with_kinships(osv.osv):
    _name = 'res.partner'
    _inherit = 'res.partner'

    def _count(self, cr, uid, student_id, father_id, mother_id):
        brothers = set()
        if father_id:
            brothers |= set(self.search(cr, uid, [('father_id', '=', father_id), ('id', '!=', student_id)]))
        if mother_id:
            brothers |= set(self.search(cr, uid, [('mother_id', '=', mother_id), ('id', '!=', student_id)]))
        return len(brothers)

    def _count_brothers(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for student in self.browse(cr, uid, ids):
            res[student.id] = self._count(cr, uid, student.id, student.father_id.id, student.mother_id.id)
        return res

    def _get_brothers(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for student in self.browse(cr, uid, ids):
            brothers = set()
            queryFather = [('id', '!=', student.id),
                           ('father_id', '!=', None),
                           ('father_id', '=', student.father_id.id)]
            brothers |= set(self.search(cr, uid, queryFather))
            queryMother = [('id', '!=', student.id),
                           ('mother_id', '!=', None),
                           ('mother_id', '=', student.mother_id.id)]
            brothers |= set(self.search(cr, uid, queryMother))
            res[student.id] = brothers and list(brothers) or []
        return res

    def onchange_parents(self, cr, uid, id, father_id=False, mother_id=False):
        return {'value': {'num_brothers': self._count(cr, uid, id, father_id, mother_id)}}

    _columns = {
        'father_id': fields.many2one('res.partner', 'Father',
                                     domain=[('is_company', '=', False), ('is_student', '=', False)],
                                     ondelete='set null'),
        'mother_id': fields.many2one('res.partner', 'Mother',
                                     domain=[('is_company', '=', False), ('is_student', '=', False)],
                                     ondelete='set null'),
        'brother_ids': fields.function(_get_brothers, method=True, type='many2many', obj='res.partner',
                                       string='Brothers'),
        'family_member_ids': fields.one2many('pedagogy.kinship', 'student_id', 'Family members',
                                             context={'invisible': [('is_student', '=', False)]}),
        'related_student_ids': fields.one2many('pedagogy.kinship', 'person_id', 'Related Students'),
        'num_brothers': fields.function(_count_brothers, method=True, type='integer', string='Number of brothers'),
    }
