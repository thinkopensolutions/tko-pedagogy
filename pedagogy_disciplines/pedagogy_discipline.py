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

from osv import fields
from osv import osv
from tools.translate import _


class pedagogy_discipline(osv.osv):
    def _is_coordinator(self, cr, uid):
        user_pool = self.pool.get('res.users')
        [user] = user_pool.browse(cr, uid, [uid])
        for group in user.groups_id:
            if group.name == u'Pedagogy / Coordinator':
                return True
        return False

    def _is_owner(self, cr, uid, ids, field_name, arg, context=None):
        if not self._is_coordinator(cr, uid):
            return dict(map(lambda id: (id, True), ids))
        res = {}
        for discipline in self.browse(cr, uid, ids, context=context):
            CDTs = discipline.class_discipline_teacher_ids
            res[discipline.id] = any(CDT.teacher_id.user_id.id == uid for CDT in CDTs)
        return res

    def write(self, cr, uid, ids, vals, context=None):
        owner = self._is_owner(cr, uid, ids, 'coordinates', None, context=context)
        cant_write = [id for (id, v) in owner.items() if not v]
        if len(cant_write) > 0:
            names = map(lambda d: d.name, self.browse(cr, uid, cant_write))
            raise osv.except_osv(_('Illegal'), _('You can\'t write to the following disciplines: ') + ','.join(names))
        return super(pedagogy_discipline, self).write(cr, uid, ids, vals, context=context)

    _name = 'pedagogy.discipline'
    _description = 'Pedagogy Disciplines'
    _columns = {
        'owner': fields.function(_is_owner, method=True, type='boolean'),
        'name': fields.char('Discipline Name', size=128, required=True,
                            help='The discipline name (ex:. Matemathic, Geography).'),
        'code': fields.char('Discipline Code', size=6, required=True, help='The discipline code (ex:. MAT, GEO).'),
        'discipline_area_id': fields.many2one('pedagogy.discipline_area', 'Discipline Area', ondelete='cascade',
                                              required=True),
        'sequence': fields.integer('Sequence', help='Set the discipline sort sequence (10,20,...). To sort in lists.'),
        'class_discipline_teacher_ids': fields.one2many('pedagogy.class.discipline.teacher', 'discipline_id', 'CDTs'),
    }

    _defaults = {
        'owner': True
    }

    _order = 'sequence, name'


class pedagogy_discipline_area_m2m(osv.osv):
    _name = 'pedagogy.discipline_area'
    _inherit = 'pedagogy.discipline_area'

    _columns = {
        'discipline_ids': fields.one2many('pedagogy.discipline', 'discipline_area_id', 'Disciplines'),
    }
