# -*- coding: utf-8 -*-

from odoo import models, fields, api

class PosPaymentMethod(models.Model):
    """
        Just a small inherit to insert the multicurrency fields
        into the payment method model
    """

    _inherit = 'pos.payment.method'

    currency_id = fields.Many2one("res.currency", "Moneda", default=lambda self: self.env.company.currency_id.id)
    currency_id_dif = fields.Many2one("res.currency", string="Moneda de referencia", related="currency_id.parent_id")
    manual_currency_exchange_rate = fields.Float(
        'Tasa del dia',
        digits=(20,10),
        compute="_compute_tasa_del_dia",
        tracking=True
    )
    has_reference = fields.Boolean("Necesita referencia")

    @api.depends('currency_id','currency_id_dif')
    def _compute_tasa_del_dia(self):
        for rec in self:
            rec.manual_currency_exchange_rate = 0.0

            if rec.currency_id_dif:
                if rec.currency_id_dif.name == 'USD':
                    rec.manual_currency_exchange_rate = rec.currency_id_dif._convert(1, rec.currency_id, rec.env.company, fields.date.today())
                elif rec.currency_id_dif.name in ['VES', 'VEF']: 
                    rec.manual_currency_exchange_rate = rec.currency_id._convert(1, rec.currency_id_dif, rec.env.company, fields.date.today())
