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

from osv import osv, fields


class account_move_line(osv.osv):
    _inherit = 'account.move.line'

    def _student(self, cr, uid, ids, name, arg, context=None):
        res_partner_obj = self.pool.get('res.partner')
        billing_obj = self.pool.get('pedagogy_billing')
        res = {}
        for line in self.browse(cr, uid, ids):
            res[line.id] = False
            if line.invoice and line.invoice.billing_ids:
                bill = [bill for bill in line.invoice.billing_ids if bill.invoice_id.id == line.invoice.id]
                res[line.id] = bill and bill[0].student_id.id
            if line.name == 'FT 13/0268':
                print ''
        return res

    def _student_search(self, cursor, user, obj, name, args, context=None):
        if not args:
            return []
        res_partner_obj = self.pool.get('res.partner')
        i = 0
        while i < len(args):
            fargs = args[i][0].split('.', 1)
            if len(fargs) > 1:
                args[i] = (fargs[0], 'in', res_partner_obj.search(cursor, user,
                                                                  [(fargs[1], args[i][1], args[i][2])]))
                i += 1
                continue
            if isinstance(args[i][2], basestring):
                res_ids = res_partner_obj.name_search(cursor, user, args[i][2], [],
                                                      args[i][1])
                args[i] = (args[i][0], 'in', [x[0] for x in res_ids])
            i += 1
        qu1, qu2 = [], []
        res = []
        for x in args:
            if x[1] != 'in':
                if (x[2] is False) and (x[1] == '='):
                    qu1.append('(i.id IS NULL)')
                elif (x[2] is False) and (x[1] == '<>' or x[1] == '!='):
                    qu1.append('(i.id IS NOT NULL)')
                else:
                    qu1.append('(i.id %s %s)' % (x[1], '%s'))
                    qu2.append(x[2])
            elif x[1] == 'in':
                if len(x[2]) > 0:
                    qu1.append('(i.id IN (%s))' % (','.join(['%s'] * len(x[2]))))
                    qu2 += x[2]
                else:
                    qu1.append(' (False)')

        # TKO: get invoicees from billing
        cursor.execute('SELECT distinct(invoicee_id) FROM pedagogy_billing ' \
                       'WHERE student_id in (%s) ', qu2)
        partners = cursor.fetchall()
        if not partners:
            return [('id', '=', '0')]
        partners_ids = [x[0] for x in partners]
        if len(partners_ids) > 1:
            cursor.execute('SELECT id ' \
                           'FROM account_move_line ' \
                           'where partner_id in %s ' % str(tuple(partners_ids)))
        else:
            cursor.execute('SELECT id ' \
                           'FROM account_move_line ' \
                           'where partner_id in (%s) ', partners_ids)
        res = cursor.fetchall()

        #        # TKO: get invoices from billing
        #        cursor.execute('SELECT distinct(l.id) ' \
        #                       'FROM account_move_line as l ' \
        #                       'inner join account_invoice as inv on l.move_id = inv.move_id ' \
        #                       'inner join pedagogy_billing as b on inv.id = b.invoice_id ' \
        #                       'inner join res_partner as i on i.id = b.student_id ' \
        #                       'where i.id in (%s) ', qu2)
        #        res += cursor.fetchall()
        if not res:
            return [('id', '=', '0')]
        # res = list(set(res))
        return [('id', 'in', [x[0] for x in res])]

    _columns = {
        'student_id': fields.function(_student, method=True, string='Student', type='many2one',
                                      domain=[('is_student', '=', True)], relation='res.partner',
                                      fnct_search=_student_search),
    }
