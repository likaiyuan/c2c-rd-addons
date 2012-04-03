# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2011 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2011 Camptocamp Austria (<http://www.camptocamp.com>).
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
from lxml import etree
import decimal_precision as dp

import netsvc
import pooler
from osv import fields, osv, orm
from tools.translate import _

class sale_order(osv.osv):
    _inherit = "sale.order"

    def _print_uom(self, cr, uid, ids, name, args, context=None):
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
	  print_uom = False
	  if order.order_line:
            for line in order.order_line:
                if not line.product_uos or line.product_uos and line.product_uom != line.product_uos:
		   print_uom = True
          res[order.id] =  print_uom
        return res

    def _print_uos(self, cr, uid, ids, name, args, context=None):
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
          print_uos = False
          if order.order_line:
            for line in order.order_line:
                if line.product_uos:
                   print_uos = True
          res[order.id] =  print_uos
        return res


    def _print_packing(self, cr, uid, ids, name, args, context=None):
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
          print_packing = False
          if order.order_line:
            for line in order.order_line:
                if line.product_packaging:
                   print_packing = True
          res[order.id] =  print_packing
        return res

    def _print_ean(self, cr, uid, ids, name, args, context=None):
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
          print_ean = False
          if order.order_line:
            for line in order.order_line:
                if line.product_id.ean13 or line.product_packaging.ean:
                   print_ean = True
          res[order.id] =  print_ean
        return res

    def _print_discount(self, cr, uid, ids, name, args, context=None):
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
          print_discount = False
          if order.order_line:
            for line in order.order_line:
                if line.discount :
                   print_discount = True
          res[order.id] =  print_discount
        return res

    def _get_cols(self, cr, uid, ids, name, args, context=None):
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
          cols = 2
          if order.print_uom:
             cols += 2
          if order.print_uos:
             cols += 2
          if order.print_packing:
             cols += 2
          if order.print_ean:
             cols += 1
          if order.print_discount:
             cols += 1
           
          res[order.id] = cols

        return res



    _columns = {
              'print_uom': fields.function(_print_uom, method=True, type='boolean', string='Print UoM if different from UoS',),
              'print_uos': fields.function(_print_uos, method=True, type='boolean', string='Print UoS if exists',),
              'print_packing': fields.function(_print_packing, method=True, type='boolean', string='Print Packing Info if available',),
              'print_ean': fields.function(_print_ean, method=True, type='boolean', string='Print EAN if available',),
              'print_discount': fields.function(_print_discount, method=True, type='boolean', string='Print Discount if available',),
              'cols': fields.function(_get_cols, method=True, type='integer', string='No of columns before totals',),
    }
sale_order()