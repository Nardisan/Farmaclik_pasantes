# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models, _, fields, api
from odoo.exceptions import ValidationError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    change = fields.Monetary(
        "Extra",
        "currency_id",
        default=0.00, 
        tracking=True,
    )
    transaction_type = fields.Selection(
        [("full", "Full"), ("change", "Change")],
        "Forma de pago", 
        default="full"
    )
    to_wallet = fields.Boolean()
    change_type = fields.Selection(
        [('wallet', 'Por wallet'), ('normal', 'Normal')],
        "Tipo de cambio",
        compute="_compute_change_type",
        tracking=True
    )
    paid = fields.Boolean()

    @property
    def date(self): return datetime.today().strftime("el %x a las %X %p")

    @api.depends("to_wallet")
    def _compute_change_type(self):
        for rec in self:
            rec.change_type = "wallet" if rec.to_wallet else "normal"

    def action_change_wallet(self):
        self.partner_id.wallet_lines.create({
            "customer_id": self.partner_id.id,
            "type": "change",
            "credit": self.change,
            "origin": "website",
        })

        self.paid = True

        self.message_post(
            body=f"Se ha agregado el cambio a la billetera del cliente {self.date}, un monto de ${self.change}"
        )

    def go_paid(self): 
        self.paid = True

        self.message_post(
            body=f"Se ha entregado el cambio al cliente {self.date}, un monto de ${self.change}"
        )
        
    def write(self, vals):
        if type(vals) != dict:
            for val in vals:
                if "to_wallet" in val and not val["to_wallet"]:
                    val["paid"] = True
        else:
            if "to_wallet" in vals and not vals["to_wallet"]:
                vals["paid"] = True

        return super().write(vals)

    def _create_payment_transaction(self, vals):
        '''Similar to self.env['payment.transaction'].create(vals) but the values are filled with the
        current sales orders fields (e.g. the partner or the currency).
        :param vals: The values to create a new payment.transaction.
        :return: The newly created payment.transaction record.
        '''

        # Ensure the currencies are the same.
        currency = self[0].pricelist_id.currency_id
        if any(so.pricelist_id.currency_id != currency for so in self):
            raise ValidationError(_('A transaction can\'t be linked to sales orders having different currencies.'))

        # Ensure the partner are the same.
        partner = self[0].partner_id
        if any(so.partner_id != partner for so in self):
            raise ValidationError(_('A transaction can\'t be linked to sales orders having different partners.'))

        # Try to retrieve the acquirer. However, fallback to the token's acquirer.
        acquirer_id = vals.get('acquirer_id')
        acquirer = False
        payment_token_id = vals.get('payment_token_id')

        if payment_token_id:
            payment_token = self.env['payment.token'].sudo().browse(payment_token_id)

            # Check payment_token/acquirer matching or take the acquirer from token
            if acquirer_id:
                acquirer = self.env['payment.acquirer'].browse(acquirer_id)
                if payment_token and payment_token.acquirer_id != acquirer:
                    raise ValidationError(_('Invalid token found! Token acquirer %s != %s') % (
                    payment_token.acquirer_id.name, acquirer.name))
                if payment_token and payment_token.partner_id != partner:
                    raise ValidationError(_('Invalid token found! Token partner %s != %s') % (
                    payment_token.partner.name, partner.name))
            else:
                acquirer = payment_token.acquirer_id

        # Check an acquirer is there.
        if not acquirer_id and not acquirer:
            raise ValidationError(_('A payment acquirer is required to create a transaction.'))

        if not acquirer:
            acquirer = self.env['payment.acquirer'].browse(acquirer_id)

        # Check a journal is set on acquirer.
        if not acquirer.journal_id:
            raise ValidationError(_('A journal must be specified for the acquirer %s.', acquirer.name))

        if not acquirer_id and acquirer:
            vals['acquirer_id'] = acquirer.id

        vals.update({
            'currency_id': currency.id,
            'partner_id': partner.id,
            'sale_order_ids': [(6, 0, self.ids)],
            'type': self[0]._get_payment_type(vals.get('type')=='form_save'),
        })

        if not "amount" in vals:
            vals["amount"] = sum(self.mapped('amount_total'))

        transaction = self.env['payment.transaction'].create(vals)

        # Process directly if payment_token
        if transaction.payment_token_id:
            transaction.s2s_do_transaction()

        return transaction