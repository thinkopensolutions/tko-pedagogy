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
    'name': 'Pedagogy Billing Account',
    'version': '0.057',
    'category': 'Pedagogy',
    'sequence': 38,
    'complexity': 'normal',
    'description': '''== Pedagogy Billing Account Module ==
Implements invoices from billing''',
    'author': 'ThinkOpen Solutions',
    'website': 'http://www.thinkopensolution.com',
    'images': ['images/oerp61.jpeg', ],
    'depends': ['pedagogy_base',
                'pedagogy_billing',
                'account', 'account_payment',
                'account_cancel',
                ],
    'init_xml': [],
    'update_xml': ['pedagogy_billing_workflow.xml',
                   'pedagogy_billing_view.xml',
                   'pedagogy_billing_report_view.xml',
                   'account_invoice_view.xml',
                   'wizard/pedagogy_billing_invoice.xml',
                   'wizard/account_invoice_refund_view.xml',
                   'security/ir.model.access.csv',
                   'billing_report.xml',
                   'account_move_line_view.xml',
                   'data/data.xml',
                   ],
    'demo_xml': [],
    'installable': True,
    'application': False,
    'certificate': '',
}
