# -*- coding: utf-8 -*-
# from odoo import http

import datetime
from typing import List
from odoo import http
from odoo.http import request
from odoo.addons.payment.controllers.portal import PaymentProcessing
from odoo.exceptions import UserError

class EuTabPayment(http.Controller):
    @http.route('/shop/partial/payment/', type="json", auth='public', website=True)
    def partial_payment(self, payments: List[dict]):
        order = request.website.sale_get_order()

        for payment in payments:
            if payment["hasRef"] and not payment.get("reference", False):
                raise UserError(f"La referencia es obligatoria para le tipo de pago {payment['provider']}")

        transactions = []

        for payment in payments:
            amount = float(payment["value"])
            ref = payment.get("reference",'N/A')

            transaction = order._create_payment_transaction({
                'acquirer_id': int(payment["id"]),
                'amount': amount,
                'date': datetime.date.today(),
                'return_url': '/shop/payment/validate',
                'state': 'done',
                'referencia_web': ref,
            })

            last_tx_id = request.session.get('__website_sale_last_tx_id')
            last_tx = request.env['payment.transaction'].browse(last_tx_id).sudo()

            if last_tx.exists():
                PaymentProcessing.remove_payment_transaction(last_tx)
                
            PaymentProcessing.add_payment_transaction(transaction)

            if transaction.acquirer_id.payment_type not in ["paypal", "zelle"]:
                transactions.append(transaction)

            if payment["provider"] == "wallet":
                order.partner_id.wallet_lines.create({
                    "customer_id": order.partner_id.id,
                    "type": "return",
                    "debit": float(payment["walletAmount"]),
                    "origin": "website",
                })

        request.session['__website_sale_last_tx_id'] = transaction.id

        return transactions[0].render_sale_button(order)

    @http.route('/shop/partial/wallet/', type="json", auth='public', website=True)
    def wallet_payment(self, amount):
        order = request.website.sale_get_order()

        order.partner_id.wallet_lines.create({
            "customer_id": order.partner_id.id,
            "type": "return",
            "debit": amount,
            "origin": "website",
        })