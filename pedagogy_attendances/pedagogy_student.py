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


class attendance_student(osv.osv):
    _name = 'res.partner'
    _inherit = 'res.partner'

    def _attendances(self, cr, uid, ids, field_names, args, context={}):
        res = {}
        absents_percentage = 0.0
        attended_percentage = 0.0
        for student in self.browse(cr, uid, ids, context=context):
            enrollments_obj = self.pool.get('pedagogy.enrollment')
            # temos de considerar as aulas que o professor faltou e as que ainda não foram dadas
            # atualizar o filtro, para já fica assim
            active_enrollments = enrollments_obj.search(cr, uid,
                                                        [('student_id', '=', student.id), ('state', '=', 'enrolled')])
            if active_enrollments:
                attendances_obj = self.pool.get('pedagogy.student.attendance')
                to_attend = attendances_obj.search(cr, uid, [('enrollment_id', 'in', active_enrollments)], count=True)
                absents_justified = attendances_obj.search(cr, uid, [('enrollment_id', 'in', active_enrollments),
                                                                     ('state', '=', 'justified')], count=True)
                absents_unjustified = attendances_obj.search(cr, uid, [('enrollment_id', 'in', active_enrollments),
                                                                       ('state', '=', 'unjustified')], count=True)
                absents = absents_justified + absents_unjustified
                if to_attend:
                    absents_percentage = (float(absents) / float(to_attend)) * 100.0
                else:
                    absents_percentage = 0.0
                attended_percentage = 100.0 - absents_percentage
                res[student.id] = {'to_attend': to_attend,
                                   'absents': absents,
                                   'absents_justified': absents_justified,
                                   'absents_unjustified': absents_unjustified,
                                   'attended_percentage': attended_percentage,
                                   'absents_percentage': absents_percentage,
                                   }
            else:
                res[student.id] = {'to_attend': 0,
                                   'absents': 0,
                                   'absents_justified': 0,
                                   'absents_unjustified': 0,
                                   'attended_percentage': 0.0,
                                   'absents_percentage': 0.0,
                                   }
        return res

    _columns = {'attendance_ids': fields.one2many('pedagogy.student.attendance', 'student_id', 'Attendances',
                                                  domain=[('state', 'in', ('justified', 'unjustified'))]),
                'history_ids': fields.one2many('pedagogy.student.attendance.history', 'student_id', 'History'),
                'to_attend': fields.function(_attendances, type='integer', method=True, multi='compute_attendances',
                                             string='To Attend'),
                'absents': fields.function(_attendances, type='integer', method=True, multi='compute_attendances',
                                           string='Absents'),
                'absents_justified': fields.function(_attendances, type='integer', method=True,
                                                     multi='compute_attendances', string='Absents Justified'),
                'absents_unjustified': fields.function(_attendances, type='integer', method=True,
                                                       multi='compute_attendances', string='Absents Unjustified'),
                'attended_percentage': fields.function(_attendances, type='float', method=True,
                                                       multi='compute_attendances', string=u'Attended [%]'),
                'absents_percentage': fields.function(_attendances, type='float', method=True,
                                                      multi='compute_attendances', string=u'Absented [%]'),
                }
