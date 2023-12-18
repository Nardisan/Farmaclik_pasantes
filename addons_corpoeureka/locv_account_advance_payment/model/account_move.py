# coding: utf-8
###########################################################################
from odoo import api
from odoo import fields, models
from odoo import exceptions
from odoo.tools.translate import _
from datetime import datetime

class AccountMove(models.Model):
    '''Esta clase es para crear en la factura el saldo de anticipo del cliente o proveedor'''
    _inherit = 'account.move'

    account_advance_ids = fields.One2many('account.advanced.payment','invoice_id')
    sum_amount_available = fields.Monetary('Anticipo Disponible', currency_field='currency_company')
    sum_amount_available_dolares = fields.Monetary('Monto moneda extranjera', currency_field='foreign_currency')
    currency_company = fields.Many2one('res.currency', string='Currency')
    foreign_currency = fields.Many2one('res.currency', string='Currency')

    @api.onchange('partner_id')
    def _onchange_amount_available(self):
        '''Muestra el saldo disponible en los anticipos para clientes y proveedores'''
        self.currency_company = self.env.company.currency_id
        self.foreign_currency = self.env['res.currency'].search([
            ('name', '=', 'USD')
        ])
        self.sum_amount_available = 0
        bolivares = 0
        dolares = 0
        sum_bolivares = 0
        advance_obj = self.env['account.advanced.payment']

        if self.move_type == 'out_invoice' or self.move_type == 'out_refund':
            advance_bw = advance_obj.search([('partner_id', '=', self.partner_id.id),
                                         ('state', '=', 'available'),
                                         ('es_cliente','=',True)])

            for advance in advance_bw:
                if advance.currency_id.id == self.env.company.currency_id.id:
                    bolivares += advance.amount_available
                else:
                    dolares += advance.amount_available
                    sum_bolivares += advance.amount_available_conversion 
            fecha = datetime.now().strftime('%Y-%m-%d')
            self.sum_amount_available = bolivares + sum_bolivares
            self.sum_amount_available_dolares = dolares
        else:
            advance_bw = advance_obj.search([('partner_id', '=', self.partner_id.id),
                                             ('state', '=', 'available'),
                                             ('es_proveedor', '=', True)])
            for advance in advance_bw:
                if advance.currency_id.id == self.env.company.currency_id.id:
                    bolivares += advance.amount_available
                else:
                    dolares += advance.amount_available
                    sum_bolivares += advance.amount_available_conversion
            fecha = datetime.now().strftime('%Y-%m-%d')
            self.sum_amount_available = bolivares + sum_bolivares
            self.sum_amount_available_dolares = dolares
        return

    @api.onchange('invoice_date')
    def onchange_invoice_date(self):
        self.sum_amount_available = 0
        bolivares = 0
        dolares = 0
        sum_bolivares = 0
        advance_obj = self.env['account.advanced.payment']

        if self.move_type == 'out_invoice' or self.move_type == 'out_refund':
            advance_bw = advance_obj.search([('partner_id', '=', self.partner_id.id),
                                             ('state', '=', 'available'),
                                             ('es_cliente', '=', True)])

            for advance in advance_bw:
                if advance.currency_id.id == self.env.company.currency_id.id:
                    bolivares += advance.amount_available
                else:
                    dolares += advance.amount_available
                    sum_bolivares += advance.amount_available_conversion
            self.sum_amount_available = bolivares + sum_bolivares
            self.sum_amount_available_dolares = dolares
        else:
            advance_bw = advance_obj.search([('partner_id', '=', self.partner_id.id),
                                             ('state', '=', 'available'),
                                             ('es_proveedor', '=', True)])
            for advance in advance_bw:
                if advance.currency_id.id == self.env.company.currency_id.id:
                    bolivares += advance.amount_available
                else:
                    dolares += advance.amount_available
                    sum_bolivares += advance.amount_available_conversion
            self.sum_amount_available = bolivares + sum_bolivares
            self.sum_amount_available_dolares = dolares
        return

