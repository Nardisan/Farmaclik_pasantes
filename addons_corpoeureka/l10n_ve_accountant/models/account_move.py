# -*- coding: utf-8 -*-

from odoo import fields, models, api

class AccountMove(models.Model):
    _inherit = "account.move"

    pass

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    payments_three = fields.Boolean(string='Payments to third parties', store=True,readonly=False) #Variable de pago a terceros

