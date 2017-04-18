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
    'name': 'Pedagogy Medical',
    'version': '0.033',
    'category': 'Pedagogy',
    'sequence': 38,
    'complexity': 'normal',
    'description': '''== Pedagogy Medical Module ==
''',
    'author': 'ThinkOpen Solutions',
    'website': 'http://www.thinkopensolution.com',
    'images': ['images/oerp61.jpeg', ],
    'depends': ['crm',
                'pedagogy_base',
                ],
    'init_xml': ['data/pedagogy.medical.bmi.qualitative.csv',
                 ],
    'update_xml': ['security/ir.model.access.csv',
                   'student_view.xml',
                   'bmi_view.xml',
                   'medical_history_view.xml',
                   ],
    'demo_xml': [],
    'installable': True,
    'application': False,
    'certificate': '',
}
