# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    Thinkopen - Portugal & Brasil
#    Copyright (C) Thinkopen Solutions (<http://www.thinkopensolutions.com>).
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
    'name': 'pedagogy_base_school_year_wizard',
    'version': '0.003',
    'category': 'pedagogy_base_school_year_wizard',
    'sequence': 38,
    'complexity': 'normal',
    'description': '''== pedagogy_base_school_year_wizard Module ==
Change this pedagogy_base_school_year_wizard description after!''',
    'author': 'ThinkOpen Solutions',
    'website': 'http://www.thinkopensolution.com',
    'images': ['images/oerp61.jpeg', ],
    'depends': ['base',
                ],
    'init_xml': [],
    'update_xml': ['pedagogy_base_school_year_wizard_view.xml',
                   'pedagogy_base_school_year_wizard_workflow.xml',
                   ],
    'demo_xml': ['pedagogy_base_school_year_wizard_demo.xml',
                 ],
    'installable': True,
    'application': True,
    'certificate': '',
}
