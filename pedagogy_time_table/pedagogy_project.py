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


class task(osv.osv):
    _inherit = 'project.task'

    def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=100):
        (a, b, ids) = args[0]
        if ids and isinstance(ids, list) and isinstance(ids[0], list):
            ids = [p[1] for p in ids]
            args[0] = (a, b, ids)
        return super(task, self).name_search(cr, user, name, args, operator, context, limit)

    _columns = {'time_table_id': fields.many2one('pedagogy.time_table', 'Time Table', ondelete='cascade'),
                }
