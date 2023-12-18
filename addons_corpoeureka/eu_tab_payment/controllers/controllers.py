# -*- coding: utf-8 -*-
# from odoo import http

import datetime
from typing import List
from odoo import http, _
from odoo.http import request
from odoo.addons.payment.controllers.portal import PaymentProcessing
from odoo.exceptions import UserError
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager

class EuTabPayment(http.Controller):
    @http.route('/shop/partial/payment/', type="json", auth='public', website=True)
    def partial_payment(self, payments: List[dict], to_wallet: bool):
        order = request.website.sale_get_order()

        for payment in payments:
            if payment["hasRef"] and not payment.get("reference", False):
                raise UserError("La referencia es obligatoria para le tipo de pago " + payment['provider'])

        for payment in payments:
            payment.update({
                "value": float(payment["value"]),
                "id": int(payment["id"]),
                "reference": payment.get("reference", 'N/A'),
                "walletAmount": float(payment.get("walletAmount", 0)),
            })

        payments = list(sorted(payments, key=lambda p: p["value"]))

        total_amount = sum(payment["value"] for payment in payments)

        amount = 0.00

        if total_amount > (order.amount_total + 0.16):
            amount = total_amount - order.amount_total
            payments[-1]["value"] -= amount

            order.update({
                "change": round(amount, 2),
                "transaction_type": "change",
                "to_wallet": to_wallet,
                "paid": False,
            })

        transaction = None

        for payment in payments:
            transaction = order._create_payment_transaction({
                'acquirer_id': payment["id"],
                'amount': payment["value"],
                'date': datetime.date.today(),
                'return_url': '/shop/payment/validate',
                'state': 'done',
                'referencia_web': payment["reference"],
            })

            transaction.amount_with_change = payment["value"]

            last_tx_id = request.session.get('__website_sale_last_tx_id')
            last_tx = request.env['payment.transaction'].browse(last_tx_id).sudo()

            if last_tx.exists():
                PaymentProcessing.remove_payment_transaction(last_tx)
                
            PaymentProcessing.add_payment_transaction(transaction)

            if payment["provider"] == "wallet":
                order.partner_id.wallet_lines.create({
                    "customer_id": order.partner_id.id,
                    "type": "return",
                    "debit": payment["walletAmount"],
                    "origin": "website",
                })

        request.session['__website_sale_last_tx_id'] = transaction.id
        transaction.amount_with_change += amount

        return transaction.render_sale_button(order)

class WalletPortal(CustomerPortal):
    _items_per_page = 20
    
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)

        partner = request.env.user.partner_id

        values.update({            
            "wallet_count": request.env["wallet.management"].search_count([('customer_id', '=', partner.id)]),
            "wallet_amount": partner.remaining_wallet_amount,
        })

        return values

    @http.route("/my/wallet", type='http', auth="user", website=True, sitemap=False)
    def wallet_info(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        partner = request.env.user.partner_id

        values = {'page_name': 'wallet'}
        domain = [('customer_id', '=', partner.id)]

        Wallet = request.env["wallet.management"]

        searchbar_sortings = {
            'create_date': {
                'label': _('Fecha'), 
                'order': 'create_date desc'
            },
            'type': {
                'label': _('Tipo de la transacción'), 
                'order': 'type'
            },
            'origin': {
                'label': _('Origen de la transacción'), 
                'order': 'origin'
            },
        }

        # default sortby order
        if not sortby:
            sortby = 'create_date'
        sort_order = searchbar_sortings[sortby]['order']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        wallet_count = Wallet.search_count(domain)

        # make pager
        pager = portal_pager(
            url="/my/wallet",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=wallet_count,
            page=page,
            step=self._items_per_page
        )

        wallet_lines = Wallet.search(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])

        values.update({
            'wallet_lines': wallet_lines,
            'page_name': 'wallet',
            'pager': pager,
            'default_url': '/my/wallet',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })

        return request.render("eu_tab_payment.wallet_client", values)
