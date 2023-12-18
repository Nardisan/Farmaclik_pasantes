# -*- coding: utf-8 -*-

from odoo import api, fields, models

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    
    @api.onchange('price_subtotal','product_qty')
    def _compute_price_unit(self):
        for record in self:
            record.price_unit = record.price_subtotal / record.product_qty if record.product_qty > 0 else record.price_unit