# -*- coding: utf-8 -*-

from odoo import fields, models,api,_

class ResCurrency(models.Model):
    _inherit = 'res.currency'

    parent_id = fields.Many2one("res.currency", 
    string="Moneda Referencia",
    default=lambda self: self.env['res.currency'].search([('name', '=', 'USD')], limit=1),)

    rate_inv = fields.Float(string="Tasa Inversa",compute="_compute_rate_inv",digits=(20,10))

    @api.depends('rate')
    def _compute_rate_inv(self):
        for rec in self:
            rec.rate_inv = 0.0
            if rec.rate != 0:
                rec.rate_inv = 1 / rec.rate 
                
    rounding = fields.Float(digits=(20,10))

    rate = fields.Float(compute='_compute_current_rate', string='Current Rate', digits=(20,10),
                        help='The rate of the currency to the currency of rate 1.')