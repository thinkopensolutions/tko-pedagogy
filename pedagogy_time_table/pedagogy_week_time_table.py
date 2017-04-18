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

from calendar import Calendar
from datetime import date, time, datetime
from dateutil.relativedelta import relativedelta

from openerp.osv import osv, fields

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

WEEKDAYS = ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')
make_tuple = lambda w: (WEEKDAYS.index(w) + 1, w)


class pedagogy_week_time_table(osv.osv):
    _name = 'pedagogy.week.time.table'
    _description = 'Pedagogy Week Time Table'

    def _hour_end(self, cr, uid, ids, field_name, arg, context):
        def hour_end(wtt):
            h = wtt.hour_start + wtt.duration
            if h > 24:
                h = h - 24
            return (wtt.id, h)

        return dict(map(hour_end, self.browse(cr, uid, ids)))

    def get_current_week(self):
        cal = Calendar(0)
        today = date.today()
        monday = today.replace(day=today.day - today.weekday())
        month = list(cal.itermonthdates(monday.year, monday.month))
        index = month.index(monday)
        return month[index:index + 7]

    def float_to_time(self, f):
        hour = int(f)
        min = int((f - hour) * 60)
        return time(hour, min)

    def time_to_float(self, t):
        decimal = t.minute / 60.0
        return t.hour + decimal

    def _dates(self, cr, uid, ids, field_name, arg, context):
        res = {}
        this_week = self.get_current_week()
        for week_table in self.browse(cr, uid, ids):
            def generate_date(week_day, hour):
                time = self.float_to_time(hour)
                day = this_week[int(week_day) - 1]
                my_date = datetime.combine(day, time).strftime(DATETIME_FORMAT)
                user_rec = self.pool.get('res.users')
                user_tz_offset = user_rec.read(cr, uid, [uid], ['tz_offset'], context=context)
                my_date = datetime.strptime(my_date, '%Y-%m-%d %H:%M:00') + relativedelta(
                    hours=-float(user_tz_offset[0]['tz_offset'][:3]))
                return my_date.strftime(DATETIME_FORMAT)

            field = field_name.replace('date', 'hour')
            hour = getattr(week_table, field)
            res[week_table.id] = generate_date(week_table.week_day, hour)
        return res

    def _get_name(self, cr, uid, ids, field_name, arg, context):
        def format_name(wtt):
            template = '{0} / {1} ({2})'
            return template.format(wtt.class_discipline_teacher_id.class_year_id,
                                   wtt.class_discipline_teacher_id.discipline_id, wtt.week_day)

        wtts = self.browse(cr, uid, ids)
        return dict(map(lambda w: (w.id, format_name(w)), wtts))

    _columns = {
        'name': fields.function(_get_name, method=True, type='char', string='Name'),
        'class_discipline_teacher_id': fields.many2one('pedagogy.class.discipline.teacher', 'Class/Discipline/Teacher',
                                                       required=True),
        'class_year_id': fields.related('class_discipline_teacher_id', 'class_year_id', string='Class', type='many2one',
                                        relation='pedagogy.class.year'),
        'discipline_id': fields.related('class_discipline_teacher_id', 'discipline', string='Discipline',
                                        type='many2one', relation='pedagogy.discipline'),
        'teacher_id': fields.related('class_discipline_teacher_id', 'teacher', string='Teacher', type='many2one',
                                     relation='hr.employee'),
        'week_day': fields.selection(map(make_tuple, WEEKDAYS), string='Weekday', required=True),
        'hour_start': fields.float('Start', required=True),
        'duration': fields.float('Duration', required=True),
        'hour_end': fields.function(_hour_end, method=True, type='float', string='End'),
        'date_start': fields.function(_dates, method=True, type='datetime'),
        'date_end': fields.function(_dates, method=True, type='datetime'),
    }
