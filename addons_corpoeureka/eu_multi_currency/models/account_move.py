# -*- coding: utf-8 -*-

from odoo import api, fields, models
from datetime import date

class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.depends('amount_total','manual_currency_exchange_rate')
    def _amount_all_usd(self):
        for record in self:
            record[("amount_ref")]    = record['amount_total']
            if record.manual_currency_exchange_rate != 0:
                record[("amount_ref")]    = record['amount_total']*record.manual_currency_exchange_rate
                record[("tasa_del_dia")]     = 1*record.manual_currency_exchange_rate
                record[("tasa_del_dia_two")] = 1/record.manual_currency_exchange_rate

    @api.depends('amount_untaxed','manual_currency_exchange_rate')
    def _compute_subtotal(self):
        for record in self:
            record[("amount_untaxed_ref")]  = record.amount_untaxed
            if record.manual_currency_exchange_rate != 0 and record.company_id.currency_id.id == record.currency_id.id:
                record[("amount_untaxed_ref")]  = record['amount_untaxed']*record.manual_currency_exchange_rate
                
    @api.depends('amount_residual_signed','manual_currency_exchange_rate')
    def _compute_residual_ref(self):
        for record in self:
            record[("amount_residual_signed_ref")] = abs(record['amount_residual_signed'])
            if record.manual_currency_exchange_rate != 0 and self.env.company.currency_id == record.currency_id:
                record[("amount_residual_signed_ref")] = abs(record['amount_residual_signed']*record.manual_currency_exchange_rate)
            else:
                record[("amount_residual_signed_ref")] = abs(record['amount_residual_signed'])

    @api.depends('amount_residual_signed_ref','amount_ref')
    def _compute_no_residual(self):
        for record in self:
            #record.amount_no_residual = 0
            record.amount_no_residual_ref = record.amount_ref - abs(record.amount_residual_signed_ref)
    #  Campos Nuevos para el calculo de la doble moneda
    tasa_del_dia                = fields.Float(store=True,readonly=True, compute="_amount_all_usd", default=0, digits=(20,10),string="Tasa del Día $") 
    tasa_del_dia_two            = fields.Float(store=True,readonly=True, compute="_amount_all_usd", default=0, digits=(20,10),string="Tasa del Día Bs") 
    amount_ref                  = fields.Float(string='Monto Ref', store=True, readonly=True, compute='_amount_all_usd', tracking=4, default=0)
    amount_untaxed_ref          = fields.Float(string='Sub Total Ref',store=True,readonly=True,compute='_compute_subtotal',tracking=4,default=0)
    amount_residual_signed_ref  = fields.Float(string='Imp Adeudado Ref',readonly=True,compute='_compute_residual_ref',tracking=4,default=0,store=True)
    currency_id_dif             = fields.Many2one(related="currency_id.parent_id",string="Moneda Referencia",)
    manual_currency_exchange_rate = fields.Float(string='Tipo de tasa manual', digits=(20,10),default=lambda self: self.env.company.currency_id.parent_id.rate)
    manual_currency_exchange_rate_inv = fields.Float(string='Tasa Excel', digits=(20,10))
    amount_no_residual_ref = fields.Float(string="Monto Abonado",compute="_compute_no_residual",store=True)
#
#    #@api.onchange('manual_currency_exchange_rate_inv')    
#    #def _compute_manual_currency_exchange_rate(self):
#    #    for rec in self:
#    #        if rec.manual_currency_exchange_rate_inv != 0:
    #            rec.manual_currency_exchange_rate = 1 / rec.manual_currency_exchange_rate_inv

    #calculo automatico para la tasa
    #@api.onchange('manual_currency_exchange_rate','currency_id')    
    #def _compute_manual_currency_exchange_rate(self):
    #    for rec in self:
#
#    #        if rec.manual_currency_exchange_rate != 0 and rec.currency_id.name != 'USD':
    #            rec.manual_currency_exchange_rate = 1 / rec.manual_currency_exchange_rate
               
    # Modificación de campos para activar la Trazabilidad        
    name            = fields.Char(track_visibility="always",)
    ref             = fields.Char(track_visibility="always",)
    date            = fields.Date(track_visibility="always",)
    invoice_date    = fields.Date(track_visibility="always",default=lambda self: fields.Date.to_string(date.today()))
    narration       = fields.Text(track_visibility="always",)
    user_id         = fields.Many2one(track_visibility="always",)
    currency_id     = fields.Many2one(track_visibility="always",)
    partner_id      = fields.Many2one(track_visibility="always",)
    invoice_user_id = fields.Many2one(track_visibility="always",)
    amount_untaxed  = fields.Monetary(track_visibility="always",)
    amount_tax      = fields.Monetary(track_visibility="always",)
    amount_total    = fields.Monetary(track_visibility="always",)
    state           = fields.Selection(track_visibility="always",)
