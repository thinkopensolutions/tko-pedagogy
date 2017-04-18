# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Thinkopen Solutions Brasil, Lda. All Rights Reserved
#    http://www.tkobr.com.
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
    'name': 'Pedagogy Evaluations',
    'version': '0.098',
    'category': 'Pedagogy',
    'sequence': 38,
    'complexity': 'normal',
    'description': '''== Pedagogy Evaluations Module ==
''',
    'author': 'ThinkOpen Solutions',
    'website': 'http://www.thinkopensolution.com',
    'images': ['images/oerp61.jpeg', ],
    'depends': ['pedagogy_base',
                'pedagogy_disciplines',
                ],
    'init_xml': [],
    'update_xml': ['security/ir.model.access.csv',
                   'pedagogy_evaluations.xml',
                   'pedagogy_evaluation_types.xml',
                   'pedagogy_classifications.xml',
                   'pedagogy_disciplines.xml',
                   'pedagogy_students.xml',
                   'pedagogy_factors.xml',
                   'report/evaluations_report_view.xml',
                   'security/pedagogy_security.xml',
                   'pedagogy_classifications_matrix.xml',
                   'pedagogy_workflow.xml',
                   ],
    'demo_xml': [
    ],
    'installable': True,
    'application': False,
    'certificate': '',
}
