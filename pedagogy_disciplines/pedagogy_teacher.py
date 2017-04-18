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


class pedagogy_teacher(osv.osv):
    _name = 'hr.employee'
    _inherit = 'hr.employee'

    _columns = {
        'class_discipline_teacher_ids': fields.one2many('pedagogy.class.discipline.teacher', 'teacher_id',
                                                        'Class/Discipline'),
        'is_teacher': fields.boolean('Teacher'),
    }


class hr_job_translate(osv.osv):
    _inherit = 'hr.job'

    _columns = {
        'name': fields.char('Job Name', size=128, required=True, select=True, translate=True),
    }
