# -*- coding: utf-8 -*-

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    currency_id_dif_line = fields.Many2one(related="order_id.currency_id.parent_id",
    string="Moneda Referencia", invisible="1")

    @api.depends('price_unit','order_id.manual_currency_exchange_rate')
    def _compute_price_unit_ref(self):

        for record in self:  
            record[("price_unit_ref")]  = record['price_unit']
            if record.display_type == False: 
                if record.order_id.manual_currency_exchange_rate != 0:
                        record[("price_unit_ref")]    = record['price_unit']*record.order_id.manual_currency_exchange_rate
                        
    price_unit_ref     = fields.Float(string='Precio Ref', store=True,readonly=True, compute='_compute_price_unit_ref', tracking=4, default=0, invisible="1",digits=(20,3))
    price_subtotal_ref = fields.Float(string='Subtotal Ref',store=True, readonly=True, default=0,compute='_compute_price_subtotal_ref',digits=(20,3))

    @api.onchange('product_id','product_uom_qty','price_unit_ref')
    def onchange_product_id_ref(self):
        for record in self:  
            record._compute_price_unit_ref()
            record[("price_subtotal_ref")] = record.product_uom_qty * record.price_unit_ref

    @api.depends('price_unit_ref','product_uom_qty')
    def _compute_price_subtotal_ref(self):
        for record in self: 
            record[("price_subtotal_ref")]   = 0 
            if record.display_type == False:
                record[("price_subtotal_ref")] = record.product_uom_qty * record.price_unit_ref
