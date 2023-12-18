# -*- coding: utf-8 -*-
from odoo import models, fields, _

class WalletManagement(models.Model):
    _inherit = "wallet.management"

    user_id = fields.Many2one("res.users", "Usuario", default=lambda self: self.env.user)
    origin = fields.Selection(
        [("pos", "POS"), ("manual", "Manual"), ("website", "Website")],
        "Origen de la transacción", 
        default="pos"
    )