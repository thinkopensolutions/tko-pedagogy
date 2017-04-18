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

from openerp.osv import osv, fields


class pedagogy_content(osv.osv):
    _name = 'pedagogy.content'
    _description = 'Pedagogy Content'

    def onchange_topic_id(self, cr, uid, ids, topic_id):
        v = {}
        if topic_id:
            topic = self.pool.get('pedagogy.topic').browse(cr, uid, topic_id)
            v['school_year_id'] = topic.school_year_id.id
            v['topic_title'] = topic.title
        return {'value': v}

    def create(self, cr, uid, vals, context=None):
        vals.update({'sequence': self.pool.get('ir.sequence').get(cr, uid, 'pedagogy.content.sequence')})
        return super(pedagogy_content, self).create(cr, uid, vals, context)

    def copy(self, cr, uid, id, vals, context=None):
        vals['task_ids'] = []
        return super(pedagogy_content, self).copy(cr, uid, id, vals, context)

    _columns = {
        'name': fields.char('Title', size=128, required=True),
        'topic_id': fields.many2one('pedagogy.topic', 'Topic', required=True),
        'school_year_id': fields.related('topic_id', 'school_year_id', type='many2one', relation='pedagogy.school.year',
                                         string='School Year'),
        'topic_title': fields.related('topic_id', 'title', type='char', string='Topic Title'),
        'group_id': fields.many2one('pedagogy.group', 'Group', required=True),
        'discipline_id': fields.many2one('pedagogy.discipline', 'Discipline', required=True),
        'content_area_id': fields.many2one('pedagogy.content_area', 'Area'),
        'objectives': fields.text('Objectives', help='Describe the theme objective usually for example one month.',
                                  required=True),
        'general_skills': fields.text('General Skills', required=True),
        'specific_skills': fields.text('Specific Skills', required=True),
        'task_ids': fields.one2many('project.task', 'content_id', 'Tasks'),
        'planned_time': fields.float('Planned Time', required=True),
        'sequence': fields.integer('Sequence'),
        'links': fields.one2many('pedagogy.content.link', 'content', 'Links'),
    }

    _order = 'sequence'

    _sql_constraints = [
        ('planned_time_check', 'check (planned_time>0)', 'The planned time must be higher than 00:00!')
    ]


class content_link(osv.osv):
    _name = 'pedagogy.content.link'

    def today(self):
        DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
        return datetime.now().strftime(DATE_FORMAT)

    def create(self, cr, uid, values, context):
        values.update({'user': uid, 'date': self.today()})
        return super(content_link, self).create(cr, uid, values, context)

    _columns = {
        'user': fields.many2one('res.users', 'User'),
        'date': fields.datetime('Date'),
        'content': fields.many2one('pedagogy.content', 'Content'),
        'url': fields.char('URL', size=1024, required=True),
        'description': fields.text('Description', required=True),
    }
