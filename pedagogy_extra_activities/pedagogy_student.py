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

from osv import osv


class pedagogy_student(osv.osv):
    _name = 'res.partner'
    _inherit = 'res.partner'

    def _latest_enrollment(self, cr, uid, ids, context=None):
        res = {}

        users = ''
        for id in ids:
            res[id] = False;
            users = users + str(id) + ','

        query = 'SELECT DISTINCT ON (res_partner.id) \
                            res_partner.id, \
                            pedagogy_enrollment.id, \
                            pedagogy_school_year.coordinator_id, \
                            pedagogy_group_area.coordinator_id, \
                            pedagogy_class_year.coordinator_id \
                        FROM \
                            res_partner \
                        INNER JOIN pedagogy_enrollment ON (res_partner.id = pedagogy_enrollment.student_id) \
                        INNER JOIN pedagogy_class_year ON (pedagogy_enrollment.class_year_id = pedagogy_class_year.id) \
                        INNER JOIN pedagogy_school_year ON (pedagogy_class_year.year_id = pedagogy_school_year.id) \
                        INNER JOIN pedagogy_class ON (pedagogy_class_year.class_id = pedagogy_class.id) \
                        INNER JOIN pedagogy_group ON (pedagogy_class.group_id = pedagogy_group.id) \
                        INNER JOIN pedagogy_group_area ON (pedagogy_group.group_area_id = pedagogy_group_area.id) \
                        INNER JOIN pedagogy_class_type ON (pedagogy_class.class_type_id = pedagogy_class_type.id) \
                        WHERE \
                            res_partner.id in ({0}) \
                            AND pedagogy_enrollment.state in {1} \
                            AND pedagogy_class_type.is_curricular = True \
                        ORDER BY \
                            res_partner.id, pedagogy_enrollment.number desc'.format(users[:-1],
                                                                                    ('enrolled', 'suspended'))

        cr.execute(query)
        result = cr.fetchall()
        for row in result:
            #            res[row[0]] = {'enrollment_id': row[1],
            #                           'year_coordinator_id': row[2],
            #                           'group_coordinator_id': row[3],
            #                           'class_coordinator_id': row[4]
            #                           }
            res[row[0]] = row[1]

        return res
