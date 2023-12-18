# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################

from odoo import http, tools, api, _, SUPERUSER_ID
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.tools.misc import formatLang
from odoo.addons import decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)

class WebsiteSale(WebsiteSale):

    def _get_mandatory_billing_fields(self):
        return request.website.show_required_address_fields('billing')

    def _get_mandatory_shipping_fields(self):
        return request.website.show_required_address_fields('shipping')

    @http.route()
    def payment(self, **post):
        if not request.env['onepage.checkout.config'].search([('is_active', '=', True)]) or post.get('onepage_call'):
            return super(WebsiteSale, self).payment(**post)
        return request.redirect('/shop/checkout')

    @http.route()
    def extra_info(self, **post):
        if not request.env['onepage.checkout.config'].search([('is_active', '=', True)]):
            return super(WebsiteSale, self).extra_info(**post)
        return request.redirect('/shop/checkout')
        
    @http.route()
    def checkout(self, **post):
        if not request.env['onepage.checkout.config'].search([('is_active', '=', True)]):
            return super(WebsiteSale, self).checkout(**post)

        # checkout page code strat --webkul
        order = request.website.sale_get_order()
        if order and order.state != 'draft':
            request.session['sale_order_id'] = None
            order = request.website.sale_get_order()
            
        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection

        if order.partner_id.id == request.website.user_id.sudo().partner_id.id:
            return request.redirect('/shop/address')

        for f in self._get_mandatory_billing_fields():
            if not order.partner_id[f]:
                return request.redirect('/shop/address?partner_id=%d' % order.partner_id.id)

        values = self.checkout_values(**post)

        values.update({'website_sale_order': order})

        # Avoid useless rendering if called in ajax
        if post.get('xhr'):
            return 'ok'
        # checkout page code end -- webkul
        
        # confirm order controller values
        order.onchange_partner_shipping_id()
        order.order_line._compute_tax_id()
        request.session['sale_last_order_id'] = order.id
        request.website.sale_get_order(update_pricelist=True)


        # Check that this option is activated
        extra_step = request.env['ir.ui.view']._view_obj('website_sale.extra_info_option')
        if extra_step.active:
            values['extra_step_active'] = True

        # payment controller values
        post.update({'onepage_call': True})
        payment_vals = self.payment(**post)
        values.update(payment_vals.qcontext)

        onepage_config_values = request.env['onepage.checkout.config'].get_config_settings_values()
        values.update(onepage_config_values)


        return request.render("website_onepage_checkout.onepage_checkout", values)

    def onepage_checkout_redirection(self, order):
        if not order or order.state != 'draft':
            request.session['sale_order_id'] = None
            request.session['sale_transaction_id'] = None
            values = {'url':'/shop', 'success': False}
            return values

        tx = request.env.context.get('website_sale_transaction')
        if tx and tx.state != 'draft':
            values = {'url':'/shop/payment/confirmation/%s' % order.id, 'success': False}
            return values


    def _format_amount(self, amount, currency):
        fmt = "%.{0}f".format(currency.decimal_places)
        lang = request.env['res.lang']._lang_get(request.env.context.get('lang') or 'en_US')
        return lang.format(fmt, currency.round(amount), grouping=True, monetary=True)\
            .replace(r' ', u'\N{NO-BREAK SPACE}').replace(r'-', u'-\N{ZERO WIDTH NO-BREAK SPACE}')


    @http.route(['/shop/onepage/confirm_order'], type='json', auth="public", website=True)
    def onepage_confirm_address(self, **post):
        SaleOrder = request.env['sale.order']
        order = request.website.sale_get_order()
        if not order:
            return [False, '/shop']

        redirection = self.onepage_checkout_redirection(order)
        if redirection:
            return [False, redirection]
        
        order._check_carrier_quotation(force_carrier_id=None)

        render_values = self._get_shop_payment_values(order, **post)

        if render_values['errors']:
            render_values.pop('acquirers', '')
            render_values.pop('tokens', '')
            
        render_result = request.env['ir.ui.view']._render_template("website_onepage_checkout.onepage_deliver_method", render_values)
        currency = order.currency_id
        price_values = {
            'success': True,
            'order_total': self._format_amount(order.amount_total, currency),
            'order_subtotal': self._format_amount(order.amount_untaxed, currency),
            'order_total_taxes': self._format_amount(order.amount_tax, currency),
            'order_total_delivery': self._format_amount(order.recompute_delivery_price, currency),
        }
        return [True, price_values, render_result]


class WebsiteSaleDelivery(WebsiteSale):
    def _update_website_sale_delivery_return(self, order, **post):
        res = super(WebsiteSaleDelivery, self)._update_website_sale_delivery_return(order,**post)
        
        res.update({
            'new_amount_delivery': order.amount_delivery,
            'new_amount_untaxed': order.amount_untaxed,
            'new_amount_tax': order.amount_tax,
            'new_amount_total': order.amount_total,
            'new_amount_total_ref': order.amount_total_ref,
        })
        
        return res
