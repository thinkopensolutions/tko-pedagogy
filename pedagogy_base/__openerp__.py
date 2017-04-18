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

{
    'name': 'Pedagogy for Education Management',
    'version': '1.251',
    'category': 'Pedagogy',
    'sequence': 1,
    'complexity': 'normal',
    'description': '''== Pedagogy Application ==
This application is for schools, and training companies management.''',
    'author': 'ThinkOpen Solutions',
    'website': 'http://www.thinkopensolution.com',
    'images': ['images/oerp61.jpeg', ],
    'depends': ['base',
                'crm',
                'hr',
                ],
    'init_xml': [],
    'data': ['security/pedagogy_groups.xml',
             'security/pedagogy_security.xml',
             'security/ir.model.access.csv',
             'pedagogy_workflow.xml',
             'pedagogy_base_view.xml',
             'pedagogy_student_sequence.xml',
             'pedagogy_class_year_view.xml',
             'pedagogy_class_view.xml',
             'pedagogy_enrollment_sequence.xml',
             'pedagogy_enrollment_view.xml',
             'pedagogy_student_view.xml',
             'pedagogy_dashboards_view.xml',
             'pedagogy_report.xml',
             'report/enrollments_report_view.xml',
             ],
    'demo_xml': [],
    'installable': True,
    'application': False,
    'certificate': '',
}
