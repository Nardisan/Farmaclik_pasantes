# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ResCompany(models.Model):
    _inherit = 'res.company'

    purchase_iva_ret_account = fields.Many2one('account.account', string='Cuenta de retención IVA proveedor')
    sale_iva_ret_account = fields.Many2one('account.account', string='Cuenta de declaracion IVA Cliente')
    journal_iva = fields.Many2one('account.journal', string='Diario del IVA')
