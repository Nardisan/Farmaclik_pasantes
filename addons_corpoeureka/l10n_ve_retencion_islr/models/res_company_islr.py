# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    #Columns
    purchase_islr_ret_account_id = fields.Many2one(comodel_name='account.account', string='Cuenta de retención ISLR proveedor')
    sale_islr_ret_account_id = fields.Many2one(comodel_name='account.account', string='Cuenta de retención ISLR cliente')
    journal_islr = fields.Many2one('account.journal', string='Diario del ISLR',readonly=False)