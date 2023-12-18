# -*- coding: utf-8 -*-
from odoo import models, api, _
from odoo.exceptions import UserError

class AccountPayment(models.Model):
    _inherit = "account.payment"

    @api.model
    def create(self, vals):
        res = super().create(vals)

        for rec in res:
            if rec.payment_transaction_id:
                rec.ref = rec.payment_transaction_id.referencia_web

        return res

class AccountMove(models.Model):
    _inherit = "account.move.line"

    @api.model
    def create(self, vals):
        res = super().create(vals)

        for rec in res: rec._onchange_currency()

        return res