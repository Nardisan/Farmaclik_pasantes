# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class PosPayment(models.Model):
    _inherit = 'pos.payment'

    @api.depends('amount','pos_order_id')
    def _compute_amount_ref(self):
        for rec in self:
            rec.amount_ref = rec.currency_id._convert(rec.amount, rec.pos_order_id.session_id.config_id.show_currency, rec.company_id, rec.pos_order_id.date_order or fields.Date.today())

    amount_ref = fields.Float(string="Importe Ref",compute="_compute_amount_ref",store=True)