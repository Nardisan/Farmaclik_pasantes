# -*- coding: utf-8 -*-

from odoo import models, fields,api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    currency_id_dif = fields.Many2one(related="currency_id.parent_id",
        string="Moneda Secundaria",store=True)
    utilidad_general = fields.Float(string='Utilidad General %', required=True, default="42")
    
   
    def inter_price(self):
        price_o=0.0
        price_u=0.0
        for record in self:
            for line in record.order_line:
                price_o=line.price_unit
                price_u=line.price_unit_ref
                line.price_unit=price_u
                line.price_unit_ref=price_u
            to_currency=record.currency_id_dif
            record.currency_id=to_currency
            if record.manual_currency_exchange_rate != 0:
                record.manual_currency_exchange_rate = 1/record.manual_currency_exchange_rate

    @api.depends('amount_total','manual_currency_exchange_rate')
    def _compute_amount_total_ref(self):
        for record in self:  
            record[("tax_today")] = 1
            record[("tax_today_two")] = 1
            record[("amount_total_ref")] = record.amount_total
            if record.manual_currency_exchange_rate != 0:
                record[("tax_today")]           = 1*record.manual_currency_exchange_rate
                record[("tax_today_two")]       = 1/record.manual_currency_exchange_rate                
                record[("amount_total_ref")]    = record['amount_total']*record.manual_currency_exchange_rate
  
    tax_today           = fields.Float(store=True,readonly=True, default=0, compute="_compute_amount_total_ref", string="Tasa del Día $") 
    tax_today_two       = fields.Float(store=True,readonly=True, default=0, compute="_compute_amount_total_ref", string="Tasa del Día Bs") 
    amount_total_ref    = fields.Float(string='Monto Ref', store=True, readonly=True, tracking=4, default=0, compute="_compute_amount_total_ref")
    manual_currency_exchange_rate = fields.Float(string='Tipo de tasa manual', digits=(20,10),default=lambda self: self.env.company.currency_id.parent_id.rate)