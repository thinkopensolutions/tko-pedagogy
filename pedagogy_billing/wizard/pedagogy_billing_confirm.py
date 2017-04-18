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

import netsvc
import pooler
from osv import osv
from tools.translate import _


class pedagogy_billing_confirm(osv.osv_memory):
    '''
        This wizard will confirm all the selected draft pedagogy billings.
        If none is selected will confirm all draft billings.
    '''
    _name = 'pedagogy.billing.confirm'
    _description = 'Confirm the selected pedagogy billings'

    def bill_confirm(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService('workflow')
        if context is None:
            context = {}
        pool_obj = pooler.get_pool(cr.dbname)
        data_bill = pool_obj.get('pedagogy.billing').read(cr, uid, context['active_ids'], ['state'], context=context)

        for record in data_bill:
            if record['state'] not in ('draft'):
                raise osv.except_osv(_('Warning'),
                                     _('Selected Bill(s) cannot be confirmed as they are not in Draft state!'))
            wf_service.trg_validate(uid, 'pedagogy.billing', record['id'], 'bill_verify_sheet', cr)
        return {'type': 'ir.actions.act_window_close'}
