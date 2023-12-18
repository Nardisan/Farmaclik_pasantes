# -*- coding: utf-8 -*-

from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    lote = fields.Char(string='Lote', help='Lote del producto.', copy=False, required=False)
    fecha_de_caducidad = fields.Datetime(string='Fecha de Caducidad', help='Fecha de caducidad del producto.', copy=False, required=False)
    utilidad = fields.Float(string='Utilidad %', compute='_compute_utilidad_por_defecto', store=True)
    coste_actual = fields.Float(string='Coste Referencia', compute='_compute_coste_actual', store=True)


    @api.depends('price_unit','order_id.manual_currency_exchange_rate')
    def _compute_price_unit_ref(self):
        for record in self:  
            record[("price_unit_ref")]  = record['price_unit']
            if record.display_type == False and record.order_id.manual_currency_exchange_rate != 0: 
                record[("price_unit_ref")]    = record['price_unit']*record.order_id.manual_currency_exchange_rate

    @api.depends('product_id')
    def _compute_utilidad_por_defecto(self):
        for record in self:  
            record.utilidad = record.utilidad if record.utilidad else record.product_id.product_tmpl_id.utilidad

    @api.depends('product_id')
    def _compute_coste_actual(self):
        for record in self:  
            record.coste_actual =  record.product_id.product_tmpl_id.standard_price
            
     
    @api.onchange('product_uom_qty','price_unit_ref')
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

    # Campos para Calcular la MultiMoneda
    price_unit_ref     = fields.Float(string='Precio Ref', store=True,  readonly=True, compute='_compute_price_unit_ref', tracking=4, default=0, invisible="1",digits=(20,3))
    price_subtotal_ref = fields.Float(string='Subtotal Ref',store=True, readonly=True, default=0,compute='_compute_price_subtotal_ref',digits=(20,3))
    currency_id_dif = fields.Many2one(related="order_id.currency_id.parent_id",
    string="Moneda Secundaria", invisible="1")
    