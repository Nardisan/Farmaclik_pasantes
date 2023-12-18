# -*- coding: utf-8 -*-

from odoo import fields, models, _
from odoo.exceptions import UserError

class AddWalletWizard(models.TransientModel):
    _name = 'add.wallet.wizard'
    _description = 'Add to wallet wizard'

    currency_id = fields.Many2one(
        "res.currency", 
        default=lambda self: self.env["res.currency"].search([("name", "=", "USD")])
    )
    amount = fields.Monetary("Monto", "currency_id")

    def add_wallet(self):
        if self.amount <= 0:
            raise UserError("El monto debe ser válido") 

        partner = self.env["res.partner"].search([("id", "=", self._context["active_id"])])

        partner.wallet_lines.create({
            "customer_id": partner.id,
            "type": "change",
            "credit": self.amount,
            "origin": "manual",
            "currency_id": self.currency_id.id
        })
        
        # return {
        #     'type': 'ir.actions.client',
        #     'tag': 'display_notification',
        #     'params': {
        #         'title': _('Notificación'),
        #         'message': _('Se ha agregado el monto a la billetera de forma exitosa'),
        #         'type': 'success',
        #         'sticky': True
        #     },
        # }