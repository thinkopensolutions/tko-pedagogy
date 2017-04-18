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
    'name': 'Pedagogy Time Table',
    'version': '0.067',
    'category': 'Pedagogy',
    'sequence': 38,
    'complexity': 'normal',
    'description': '''== Pedagogy Time Table Module ==
''',
    'author': 'ThinkOpen Solutions',
    'website': 'http://www.thinkopensolution.com',
    'images': ['images/oerp61.jpeg', ],
    'depends': ['pedagogy_base',
                'pedagogy_content_management',
                'pedagogy_disciplines',
                'pedagogy_evaluations',
                ],
    'init_xml': [],
    'data': ['pedagogy_menu_view.xml',
             'pedagogy_project_view.xml',
             'pedagogy_time_table_view.xml',
             'pedagogy_week_time_table_view.xml',
             'pedagogy_non_lective_days_view.xml',
             'security/ir.model.access.csv',
             'security/time_table_security.xml',
             ],
    'demo_xml': [],
    'installable': True,
    'application': False,
    'certificate': '',
}
