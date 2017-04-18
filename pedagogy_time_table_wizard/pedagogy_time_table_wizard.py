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

import time

import netsvc
from osv import osv, fields
from tools.translate import _

STATES = [
    ('draft', _('Draft')),
    ('done', _('Done')),
    ('cancel', _('Canceled')),
]

PRIORITIES = [
    ('5', _('Highest')),
    ('4', _('High')),
    ('3', _('Normal')),
    ('2', _('Low')),
    ('1', _('Lowest')),
]


class pedagogy_time_table_wizard(osv.osv):
    _name = 'pedagogy_time_table_wizard'
    # _inherit = 'res.partner'
    _description = _('pedagogy_time_table_wizard Module')

    _columns = {'name': fields.char(_('Name'), size=64, select=True, required=True, readonly=True,
                                    states={'draft': [('readonly', False)]}, help=_('Name Help String')),
                'state': fields.selection(STATES, _('State'), select=True, required=True, readonly=True,
                                          help=_(' * The \'Draft\' state is used when a user is encoding. \
                            \n* The \'Open\' state is used when user confirm this. \
                            \n* The \'Canceled\' state is used when user cancel this.')),
                'priority': fields.selection(PRIORITIES, _('Priority'), select=True, required=True, readonly=True,
                                             states={'draft': [('readonly', False)]}, help=_('Priority Help String')),
                'partner_id': fields.many2one('res.partner', _('Partner'), select=True, required=True, readonly=True,
                                              states={'draft': [('readonly', False)]}, help=_('Partner Help String')),
                'date_start': fields.date(_('Initial Data'), select=True, required=True, readonly=True,
                                          states={'draft': [('readonly', False)]}, help=_('Initial Data Help String')),
                'date_stop': fields.date(_('Final Data'), select=True, readonly=True,
                                         states={'draft': [('readonly', False)]}, help=_('Final Data Help String')),
                'amount': fields.float(_('Amount'), select=True, readonly=True, states={'draft': [('readonly', False)]},
                                       help=_('Amount Help String')),
                'image': fields.binary(_('Image')),
                'color': fields.integer(_('Color Index')),
                'observations': fields.text(_('Observations'), size=128, select=True, readonly=True,
                                            states={'draft': [('readonly', False)]}, help=_('Observation Help String'))
                }
    _defaults = {'state': 'draft',
                 'amount': 0.0,
                 'date_start': time.strftime('%Y-%m-%d'),
                 'priority': '3',
                 }
    _order = 'priority asc, date_start, name, amount desc'

    def wf_done(self, cr, uid, ids, context={}):
        obj = self.browse(cr, uid, ids[0], context)
        self.write(cr, uid, ids, {'state': 'done'})
        message = _("The '%s' has been done.") % obj.name
        self.log(cr, uid, obj.id, message)
        return True

    def wf_cancel(self, cr, uid, ids, context={}):
        obj = self.browse(cr, uid, ids[0], context)
        self.write(cr, uid, ids, {'state': 'cancel'})
        message = _("The '%s' has been canceled.") % obj.name
        self.log(cr, uid, obj.id, message)
        return True

    def action_done(self, cr, uid, ids, context={}):
        """Mark the state as done
        This method is called by kanban only and must trigger workflow
        """
        obj = self.browse(cr, uid, ids[0], context)
        wf_service = netsvc.LocalService("workflow")
        wf_service.trg_validate(uid, 'pedagogy_time_table_wizard', obj.id, 'sign_done', cr)
        return True

    def action_cancel(self, cr, uid, ids, context={}):
        """Mark the state as cancel
        This method is called by kanban only and must trigger workflow
        """
        obj = self.browse(cr, uid, ids[0], context)
        wf_service = netsvc.LocalService("workflow")
        wf_service.trg_validate(uid, 'pedagogy_time_table_wizard', obj.id, 'sign_cancel', cr)
        return True
