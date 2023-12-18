# -*- coding: utf-8 -*-
from odoo import models, fields

class AccountTax(models.Model):
    _inherit = 'account.tax'

    ret = fields.Boolean(
        string='Retención',
        help="indica si el impuesto puede ser retenido")
    wh_vat_collected_account_id = fields.Many2one(
        'account.account',
        string="Cuenta de Retención",
        help="esta cuenta sera usada para aplicar retenciones de impuesto")
    wh_vat_paid_account_id = fields.Many2one(
        'account.account',
        string="Cuenta de Retención para devoluciones",
        help="Esta cuenta sera utilizada para aplicar una retención a una devolución")

