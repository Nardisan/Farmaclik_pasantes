# -*- coding: utf-8 -*-

from odoo import api,fields, models
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    currency_id = fields.Many2one('res.currency', invisible=False,readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},store=True, force_save=True)

    currency_id_dif = fields.Many2one(related="currency_id.parent_id",
        string="Moneda Referencia",store=True)
    
    @api.depends('amount_total','manual_currency_exchange_rate')
    def _compute_amount_total_ref(self):
        for record in self:
            record[("amount_total_ref")]    =  record.amount_total
            record[("tax_today")]           =  0 
            record[("tax_today_two")]       =  0 
            if record.currency_id_dif:
                if record.manual_currency_exchange_rate != 0:
                        record[("amount_total_ref")]    = record['amount_total']*record.manual_currency_exchange_rate
                        #record[("amount_total_ref")]    = sum(record.order_line.mapped('price_subtotal_ref'))
                        record[("tax_today")]           = 1*record.manual_currency_exchange_rate
                        record[("tax_today_two")]       = 1/record.manual_currency_exchange_rate

    def inter_price(self):
        price_u=0.0
        for record in self:
            for line in record.order_line:
                price_u=line.price_unit_ref
                line.price_unit=price_u
                line.price_unit_ref=price_u
            to_currency=record.currency_id_dif
            record.currency_id=to_currency
            if record.manual_currency_exchange_rate != 0:
                record.manual_currency_exchange_rate = 1/record.manual_currency_exchange_rate

    tax_today           = fields.Float(store=True,readonly=True, default=0,digits=(20,10),string='Tasa del Día $') 
    tax_today_two       = fields.Float(store=True,readonly=True, default=0,digits=(20,10),string='Tasa del Día Bs') 
    amount_total_ref    = fields.Float(string='Monto Ref', store=True, readonly=True, compute='_compute_amount_total_ref', tracking=4, default=0)
    manual_currency_exchange_rate = fields.Float(string='Tipo de tasa manual', digits=(20,10),default=lambda self: 1/self.env.company.currency_id.parent_id.rate)
    
    def _prepare_invoice(self):
        result = super(SaleOrder, self)._prepare_invoice()
        result.update({
            'currency_id': self.currency_id.id,
            })
        return result

    @api.onchange('currency_id')
    def onchange_manual_currency_exchange(self):
        for rec in self:
            if rec.currency_id == self.env.company.currency_id:
                rec.manual_currency_exchange_rate = self.env.company.currency_id.parent_id.rate
            else:
                rec.manual_currency_exchange_rate = 1 / self.env.company.currency_id.parent_id.rate

    def _cart_update(self, product_id=None, line_id=None, add_qty=0, set_qty=0, **kwargs):
        res = super(SaleOrder, self)._cart_update(product_id=product_id, line_id=line_id, add_qty=add_qty, set_qty=set_qty, **kwargs)
        self.onchange_manual_currency_exchange()
        return res