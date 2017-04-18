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

from openerp.osv import osv, fields


class pedagogy_topic(osv.osv):
    _name = 'pedagogy.topic'
    _description = 'Pedagogy Content Topic'

    _columns = {
        'school_year_id': fields.many2one('pedagogy.school.year', 'School Year', required=True),
        'name': fields.char('Name', size=128, required=True, select=1,
                            help='This is the topic name, or ususally the month reference (ex:. September).'),
        'title': fields.char('Topic Title', size=128, required=True, select=1,
                             help='This is a short description of topic.'),
        'sequence': fields.integer('Sequence', help='Set the month sequence (1,2,...), to sort the topics in list.'),
    }

    _order = 'school_year_id, sequence, name'
