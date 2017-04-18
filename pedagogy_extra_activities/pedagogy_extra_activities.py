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


class pedagogy_class_type(osv.osv):
    _name = 'pedagogy.class.type'
    _columns = {
        'name': fields.char(_('Name'), size=128, required=True),
        'is_curricular': fields.boolean('Is Curricular?'),
    }

    _defaults = {
        'is_curricular': True,
    }


class pedagogy_class_with_type(osv.osv):
    _name = 'pedagogy.class'
    _inherit = 'pedagogy.class'
    _description = 'Pedagogy Classes'

    _columns = {
        'class_type_id': fields.many2one('pedagogy.class.type', 'Class Type', required=True),
    }


class pedagogy_class_year_with_type(osv.osv):
    _name = 'pedagogy.class.year'
    _inherit = 'pedagogy.class.year'
    _description = 'Pedagogy Class Year'

    _columns = {
        'class_type_id': fields.related('class_id', 'class_type_id', type='many2one', relation='pedagogy.class.type',
                                        readonly=True, string='Class Type', help='Class type.'),
    }
