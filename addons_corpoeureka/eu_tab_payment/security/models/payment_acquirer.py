# -*- coding: utf-8 -*-
from collections import Counter
import logging
from odoo import models, fields, api,_
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class PaymentAcquirer(models.Model):
    _inherit = "payment.acquirer"

    currency_id = fields.Many2one("res.currency")
    currency_id_dif = fields.Many2one(related="currency_id.parent_id")
    payment_type = fields.Selection([
        ("efectivo", "Efectivo"),
        ("pago_movil", "Pago movil"),
        ("transferencia", "Transferencia"),
        ("paypal", "Paypal"),
        ("zelle", "Zelle"),
        ("billetera", "Billetera"),
    ], "Payment type")
    manual_currency_exchange_rate = fields.Float(
        'Tasa del dia',
        digits=(20,10),
        compute="_compute_tasa_del_dia",
        tracking=True
    )
    provider = fields.Selection(
        selection_add=[('wallet', 'Wallet')],
        ondelete={'wallet': 'set default'}
    )
    has_reference = fields.Boolean("Necesita referencia")

    @api.onchange("provider")
    def _onchange_provider(self):
        for rec in self:
            if rec.provider == "wallet":
                rec.payment_type = "billetera"

    @api.depends('currency_id','currency_id_dif')
    def _compute_tasa_del_dia(self):
        for rec in self:
            rec.manual_currency_exchange_rate = 0.0

            if rec.currency_id_dif:
                if rec.currency_id_dif.name == 'USD':
                    rec.manual_currency_exchange_rate = rec.currency_id_dif._convert(1, rec.currency_id, rec.env.company, fields.date.today())
                elif rec.currency_id_dif.name in ['VES', 'VEF']: 
                    rec.manual_currency_exchange_rate = rec.currency_id._convert(1, rec.currency_id_dif, rec.env.company, fields.date.today())

class PaymentTransaction(models.Model):
    _inherit = "payment.transaction"

    referencia_web = fields.Char("Referencia")

    def _check_amount_and_confirm_order(self):
        self.ensure_one()
        for order in self.sale_order_ids.filtered(lambda so: so.state in ('draft', 'sent')):
            if order.currency_id.compare_amounts(sum(order.mapped("transaction_ids.amount")), order.amount_total) == 0:
                order.with_context(send_email=True).action_confirm()
            else:
               _logger.warning(
                   '<%s> transaction AMOUNT MISMATCH for order %s (ID %s): expected %r, got %r',
                   self.acquirer_id.provider,order.name, order.id,
                   order.amount_total, self.amount,
               )
               order.message_post(
                   subject=_("Amount Mismatch (%s)", self.acquirer_id.provider),
                   body=_("The order was not confirmed despite response from the acquirer (%s): order total is %r but acquirer replied with %r.") % (
                       self.acquirer_id.provider,
                       order.amount_total,
                       self.amount,
                   )
               )