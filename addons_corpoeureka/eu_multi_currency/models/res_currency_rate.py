# -*- coding: utf-8 -*-

from odoo import fields, models,api,_

class ResCurrencyRate(models.Model):
    _inherit = 'res.currency.rate'

    rate_inv = fields.Float(string="Tasa Inversa",compute="_compute_rate_inv",digits=(20,10))

    @api.depends('rate')
    def _compute_rate_inv(self):
        for rec in self:
            rec.rate_inv = 0.0
            if rec.rate != 0:
                rec.rate_inv = 1 / rec.rate 

    rate = fields.Float(digits=(20,10), default=1.0, help='The rate of the currency to the currency of rate 1')