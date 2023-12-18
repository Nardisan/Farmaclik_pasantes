# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from math import copysign


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'
    
    amount_usd = fields.Monetary('Importe USD', required=True, default=0.0, currency_field='currency_id_dif')
    currency_id_dif = fields.Many2one("res.currency", 
        string="Divisa de Referencia",
        default=lambda self: self.env['res.currency'].search([('name', '=', 'USD')], limit=1),)
    @api.onchange('product_id', 'product_uom_id', 'unit_amount', 'currency_id')
    def on_change_unit_amount_usd(self):
        user_currency = self.env['res.currency'].search([('name', '=', 'USD')], limit=1)
        if not self.product_id:
            return {}

        result_usd = 0.0
        unit = self.product_uom_id

        # Compute based on pricetype
        amount_unit = self.product_id.price_compute('standard_price', uom=unit)[self.product_id.id]
        amount_usd = amount_unit * self.unit_amount or 0.0
        result_usd = (user_currency.round(amount_usd) if user_currency else round(amount_usd, 2)) * -1
        self.amount_usd = result_usd
