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


class student(osv.osv):
    _name = 'res.partner'
    _inherit = 'res.partner'

    _columns = {'medical_history_ids': fields.one2many('pedagogy.medical.history', 'student_id', 'Medical History'),
                'bmi_ids': fields.one2many('pedagogy.medical.bmi', 'student_id', 'BMIs'),
                'physician_id': fields.many2one('res.partner', 'Physician'),
                'insurance_company_id': fields.many2one('res.partner', 'Insurance Company'),
                'plan_type': fields.char('Appolice Type', size=256),
                'appolice': fields.char('Appolice', size=256),
                'hospital_id': fields.many2one('res.partner', 'Hospital'),
                }
