# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2012 Camptocamp Austria (<http://www.camptocamp.at>)
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

from osv import fields, osv
from tools.translate import _
import logging

class c2c_budget_create(osv.osv_memory):
    """
    create budget items and lines from previous accounting periods
    """
    _name = "c2c_budget.create"
    _description = "Create Budget Wizard"
    
    _columns = {
        'budget_version_id'  : fields.many2one('c2c_budget.version','Budget Version', required=True),
        'period_from': fields.many2one('account.period', 'Start period', required=True),
        'period_to': fields.many2one('account.period', 'End period', required=True),
        'replace_lines': fields.boolean('Replace Existing Budget Lines'),
    }
    _defaults = {
        }


    def c2c_budget_create(self, cr, uid, ids, context=None):
        _logger = logging.getLogger(__name__)
        
        period_obj = self.pool.get('account.period')
        budget_item_obj = self.pool.get('c2c_budget.item')
        budget_version_obj = self.pool.get('c2c_budget.version')
        budget_lines_obj = self.pool.get('c2c_budget.line')
        if context is None:
            context = {}
        if context.get('currency_id'):
            currency_id = context['currency_id']
        else:
            currency_id = self.pool.get('res.users').browse(cr, uid, uid, context).company_id.currency_id.id
        data = self.read(cr, uid, ids, [], context=context)[0]
        budget_item_obj.budget_item_create(cr, uid, context)
        budget_version_id = data['budget_version_id'][0]
        context['version_id'] = budget_version_id
        for version in budget_version_obj.browse(cr, uid, [budget_version_id], context):
            start_date = version.budget_id.start_date
            end_date = version.budget_id.end_date
            company_id = version.company_id.id
        _logger.info('FGF version date %s %s' % (start_date,end_date))
        _logger.info('FGF version context %s' % (context))
        periods_new = period_obj.search(cr, uid, [('company_id','=',company_id), ('date_start','>=',start_date), ('date_stop','<=',end_date)])
        _logger.info('FGF periods_new %s' % (periods_new))
        periods = []
        if data['period_from'] and data['period_to']:
            periods = period_obj.build_ctx_periods(cr, uid, data['period_from'][0], data['period_to'][0])
        if periods:
            _logger.info('FGF periods %s' % (periods))

            cr.execute("""select p.id ,pn.id 
                            from account_period p,
                                 account_period pn
                           where p.id in (%s)
                             and pn.id in (%s)
                             and to_char(p.date_start,'MM') = to_char(pn.date_start,'MM')
                           """ % (','.join(map(str,periods)) , ','.join(map(str,periods_new))))
            period_map = dict(cr.fetchall())
            _logger.info('FGF period_map %s' % (period_map))
            val = {'budget_version_id': data['budget_version_id'][0],
                   'currency_id' : currency_id,
                   'name' : _('Sum Prev Period'),
                   }
            vals =[]

            cr.execute("""
select -sum(l.debit-l.credit) as amount, l.analytic_account_id, budget_item_id, l.period_id
  from account_move_line l,
       c2c_budget_item_account_rel r
where l.period_id in (%s)
  and r.account_id = l.account_id
group by l.analytic_account_id, budget_item_id, l.period_id""" % (','.join(map(str,periods))))
            
            for line in cr.dictfetchall():
                _logger.info('FGF line %s' % ( line))
                val.update(line)
                val['period_id'] =  period_map[line['period_id']]
                vals.append(val)
                _logger.info('FGF budget line %s' % (val))
                budget_lines_obj.create(cr, uid, val)
            #_logger.info('FGF line vals %s' % (vals))
            #if vals:
            #    budget_lines_obj.create(cr, uid, vals)
                 
c2c_budget_create()
       