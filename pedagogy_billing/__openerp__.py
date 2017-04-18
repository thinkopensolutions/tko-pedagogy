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
    'name': 'Pedagogy Billing',
    'version': '0.165',
    'category': 'Pedagogy',
    'sequence': 38,
    'complexity': 'normal',
    'description': '''== Pedagogy Billing Module ==
''',
    'author': 'ThinkOpen Solutions',
    'website': 'http://www.thinkopensolution.com',
    'images': ['images/oerp61.jpeg', ],
    'depends': ['account',
                'pedagogy_base',
                'hr_payroll',
                ],
    'init_xml': [],
    'update_xml': ['security/pedagogy_billing_security.xml',
                   'security/ir.model.access.csv',
                   'pedagogy_billing_workflow.xml',
                   'wizard/pedagogy_billing_by_students.xml',
                   'wizard/pedagogy_billing_by_class.xml',
                   'hr_payroll_view.xml',
                   'pedagogy_billing_sequence.xml',
                   'pedagogy_billing_view.xml',
                   'pedagogy_enrollment_view.xml',
                   'billing_report.xml',
                   'pedagogy_base_view.xml',
                   'pedagogy_billing_report_view.xml',
                   'pedagogy_people_view.xml',
                   'data/data.xml',
                   'report/enrollments_report_view.xml',
                   'wizard/pedagogy_billing_confirm_view.xml',
                   ],
    'demo_xml': [],
    'installable': True,
    'application': False,
    'certificate': '',
}
