# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Thinkopen Solutions, Lda. All Rights Reserved
#    http://www.thinkopensolutions.com.
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import osv, fields


class pedagogy_activity(osv.osv):
    _name = 'pedagogy.activity'
    _description = 'Pedagogy Activities'

    def _date_from(self, cr, uid, ids, field_name, arg, context):
        res = []
        for line in self.browse(cr, uid, ids):
            res.append((line.id, line.time_table_id.date_from))
        return dict(res)

    def _date_to(self, cr, uid, ids, field_name, arg, context):
        res = []
        for line in self.browse(cr, uid, ids):
            res.append((line.id, line.time_table_id.date_to))
        return dict(res)

    _columns = {
        'name': fields.text('Activity', required=True, select=1),
        'date_from': fields.function(_date_from, method=True, type='datetime', string='Date From', select=1,
                                     help='Read only field, start date.'),
        'date_to': fields.function(_date_to, method=True, type='datetime', string='Date To', select=2,
                                   help='Read only field, end date.'),
        'time_table_id': fields.many2one('pedagogy.time_table', 'Time Table', select=2, required=True),
    }

    _order = 'time_table_id, name'
