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


class pedagogy_medical_history(osv.osv):
    _name = 'pedagogy.medical.history'

    _columns = {
        'student_id': fields.many2one('res.partner', 'Student', domain=[('is_student', '=', True)], required=True),
        'user_id': fields.many2one('res.users', 'User', required=True),
        'date': fields.datetime('Date', required=True),
        'issue': fields.text('Issue', required=True),
        'action': fields.text('Action', required=True),
        }

    _defaults = {'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                 'user_id': lambda self, cr, uid, context=None: uid,}

    _order = 'date desc'
