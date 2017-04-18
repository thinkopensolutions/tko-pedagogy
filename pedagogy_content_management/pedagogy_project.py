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

from collections import defaultdict

from osv import fields
from osv import osv


class task(osv.osv):
    _inherit = 'project.task'

    _columns = {'content_id': fields.many2one('pedagogy.content', 'Content', ondelete='cascade'),
                }

    def update_planned_hours(self, cr, uid, ids, content_id, context=None):
        try:
            content_pool = self.pool.get('pedagogy.content')
            [content] = content_pool.browse(cr, uid, [content_id])
            values = {'planned_hours': content.planned_time,
                      'sequence': content.sequence}
            return {'value': values}
        except ValueError:
            return {}


class project(osv.osv):
    _name = 'project.project'
    _inherit = 'project.project'
    _parent_name = 'project_parent_id'

    def _children(self, cr, uid, ids, field_name, arg, context=None):
        parents = self._get_project_and_children(cr, uid, ids, context)
        children = reverse_dict(parents)
        return children

    def _parent(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for project in self.browse(cr, uid, ids):
            try:
                query = [('analytic_account_id', '=', project.analytic_account_id.parent_id.id)]
                [parent] = self.search(cr, uid, query)
                res[project.id] = parent
            except ValueError:
                pass
        return res

    _columns = {
        'project_name': fields.related('analytic_account_id', 'name', type='char', string='Project Name'),
        'project_parent_id': fields.function(_parent, method=True, store=True, type='many2one',
                                             relation='project.project'),
        'project_children': fields.function(_children, method=True, type='one2many', relation='project.project'),
    }


def reverse_dict(d):
    result = defaultdict(list)
    for a, b in d.items():
        result[b].append(a)
    return result
