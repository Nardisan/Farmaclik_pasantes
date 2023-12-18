from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero, float_compare

from itertools import groupby

class pos_config(models.Model):
	_inherit = 'pos.config'

	allow_pos_lot = fields.Boolean('Allow POS Lot/Serial Number', default=True)
	allow_auto_select_lot = fields.Boolean('Allow Auto select Lot/Serial Number', default=True)
	lot_expire_days = fields.Integer('Product Lot/Serial expire days.', default=1)
	pos_lot_receipt = fields.Boolean('Print Lot/Serial on receipt',default=1)


class account_move_line(models.Model):
	_inherit = 'account.move.line'

	lot_ids = fields.Many2many('stock.production.lot',string="Lots")
	pos_lot_ids = fields.Many2many('pos.pack.operation.lot',string="POS Lots")

class pos_order(models.Model):
	_inherit = 'pos.order'

	def _prepare_invoice_line(self, order_line):
		res  = super(pos_order, self)._prepare_invoice_line(order_line)
		lots = order_line.pack_lot_ids.mapped('lot_name')
		lot_rec = self.env['stock.production.lot'].search([('name','in',lots)])
		res.update({
			'lot_ids': [(6, 0, lot_rec.ids)],
			'pos_lot_ids' : [(6, 0, order_line.pack_lot_ids.ids)],
		})
		return res


class stock_production_lot(models.Model):
	_inherit = "stock.production.lot"

	total_available_qty = fields.Float("Total Qty", compute="_computeTotalAvailableQty")

	def _computeTotalAvailableQty(self):
		for record in self:
			move_line = self.env['stock.move.line'].search([('lot_id','=',record.id)])
			record.total_available_qty = 0.0
			for rec in move_line:
				if rec.location_dest_id.usage in ['internal', 'transit']:
					record.total_available_qty += rec.qty_done
				else:
					record.total_available_qty -= rec.qty_done
