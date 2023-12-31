# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from datetime import date, datetime
import random


class PosOrderLineInherit(models.Model):
	_inherit = 'pos.order.line'

	original_line_id = fields.Many2one('pos.order.line', string="original Line")
	return_qty = fields.Float('Return Qty')
	

class pos_order(models.Model):
	_inherit = 'pos.order'

	pos_order_date = fields.Date('Oder Date', compute='get_order_date')
	barcode = fields.Char(string="Order Barcode")
	barcode_img = fields.Binary('Order Barcode Image')
	return_order_ref = fields.Many2one('pos.order',string="Return Order Ref")
	location_id = fields.Many2one(
		comodel_name='stock.location',related='config_id.stock_location_id',
		string="Location", store=True,readonly=True)

	
	def get_order_date(self):
		for order in self:
			order.pos_order_date = order.date_order.date()

	@api.model
	def _order_fields(self, ui_order):
		res = super(pos_order, self)._order_fields(ui_order)
		code =(random.randrange(1111111111111,9999999999999))
		config = self.env['pos.session'].browse(ui_order['pos_session_id']).config_id
		res['barcode'] = ui_order.get('barcode',code)

		if 'return_order_ref' in ui_order:
			if ui_order.get('return_order_ref') != False:
				res['return_order_ref'] = int(ui_order['return_order_ref'])
				po_line_obj = self.env['pos.order.line']
				for l in ui_order['lines']:
					line = po_line_obj.browse(int(l[2]['original_line_id']))
					if line:
						line.write({
							'return_qty' : line.return_qty - (l[2]['qty']),
						})
		return res


	def print_pos_receipt(self):
		orderlines = []
		paymentlines = []
		discount = 0
		articulo = 0

		for orderline in self.lines:
			new_vals = {
				'product_id': orderline.product_id.name,
				'total_price' : round(orderline.price_subtotal_incl_ref, 2),
				'qty': orderline.qty,
				'price_unit': round(orderline.price_unit_ref,2),
				'discount': orderline.discount,
				}
			
			articulo += orderline.qty

			discount += (orderline.price_unit * orderline.qty * orderline.discount) / 100
			orderlines.append(new_vals)

		for payment in self.payment_ids:
			if payment.amount > 0:
				temp = {
					'amount': payment.amount,
					'name': payment.payment_method_id.name
				}
				paymentlines.append(temp)

		customer = self.partner_id

		vals = {
			'discount': discount,
			'orderlines': orderlines,
			'paymentlines': paymentlines,
			'change': self.amount_return,
			'subtotal': self.amount_total_ref - self.amount_tax_ref,
			'tax': self.amount_tax,
			'barcode': self.barcode,
			'user_name' : self.user_id.name,
			'customer':customer.name,
			'cedula': customer.cedula,
			'articulo': articulo,
			'vat':customer.vat,
		}

		return vals



