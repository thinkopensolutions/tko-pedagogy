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
    'name': 'Pedagogy Attendances',
    'version': '0.049',
    'category': 'Pedagogy',
    'sequence': 38,
    'complexity': 'normal',
    'description': '''== Pedagogy Attendances Module ==
''',
    'author': 'ThinkOpen Solutions',
    'website': 'http://www.thinkopensolution.com',
    'images': ['images/oerp61.jpeg', ],
    'depends': ['pedagogy_base',
                'pedagogy_content_management',
                'pedagogy_time_table',
                ],
    'init_xml': [],
    'data': [
        'security/ir.model.access.csv',
        'pedagogy_attendances_view.xml',
        'pedagogy_attendances_report_view.xml',
        'pedagogy_time_table_view.xml',
        'pedagogy_student.xml',
    ],
    'demo_xml': [],
    'installable': True,
    'application': False,
    'certificate': '',
}
