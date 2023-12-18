# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import binascii

from odoo import fields, http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.portal.controllers.mail import _message_post_helper
# from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
from odoo.addons.portal.controllers.portal import get_records_pager
from odoo.addons.purchase.controllers.portal import CustomerPortal
from functools import partial
from odoo.tools import formatLang


class CustomerPortal(CustomerPortal):

    @http.route(['/my/purchase/<int:order_id>/update_line'], type='json',
                auth="public", website=True)
    def po_line_update(
            self, line_id, remove=False, unlink=False, order_id=None,
            access_token=None, **post):
        values = self.update_line_dict(line_id, remove, unlink, order_id,
                                       access_token, **post)
        if values:
            return [values['order_line_price_unit'], values['order_amount_total']]
        return values

    @http.route(['/my/purchase/<int:order_id>/update_line_dict'], type='json',
                auth="public", website=True)
    def po_line_update_dict(
            self, order_id, remove=False, unlink=False,
            line_id=None, access_token=None, input_price=False, **kwargs):
        try:
            order_sudo = self._document_check_access(
                'purchase.order', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        if order_sudo.state not in ('draft', 'sent'):
            return False
        order_line = request.env['purchase.order.line'].sudo().browse(int(line_id))
        if order_line.order_id != order_sudo:
            return False
        if unlink:
            order_line.unlink()
            return False

        if input_price is not False:
            price = input_price
        else:
            number = -1 if remove else 1
            price = order_line.price_unit + number

        if price < 0:
            price = 0.0
        order_line.write({'price_unit': price})
        currency = order_sudo.currency_id
        format_price = partial(formatLang, request.env,
                               digits=currency.decimal_places)

        results = {
            'order_line_price_unit': format_price(price),
            'order_line_price_total': format_price(order_line.price_total),
            'order_line_price_subtotal': format_price(order_line.price_subtotal),
            'order_amount_total': format_price(order_sudo.amount_total),
            'order_amount_untaxed': format_price(order_sudo.amount_untaxed),
        }
        try:
           #results['order_totals_table'] = request.env['ir.ui.view'].render_template('purchase_rfq_online.purchase_order_portal_content_totals_table', {'purchase_order': order_sudo})
        	return results
        except ValueError:
            pass
        return results

    @http.route(['/my/purchase/<int:order_id>'], type='http', auth="public", website=True)
    def portal_my_purchase_order(self, order_id=None, report_type=None,
            access_token=None, message=False, download=False, **kw):
        try:
            order_sudo = self._document_check_access('purchase.order', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        
        if report_type in ('html', 'pdf', 'text'):
            report_xml_id = 'purchase.report_purchase_quotation'
            if order_sudo.state not in ('draft', 'sent', 'cancel'):
                report_xml_id = 'purchase.action_report_purchase_order'
            return self._show_report(
                model=order_sudo, report_type=report_type,
                report_ref=report_xml_id, download=download)

        # use sudo to allow accessing/viewing orders for public user
        # only if he knows the private token
        now = fields.Date.today()

        # Log only once a day
        if order_sudo and request.session.get(
            'view_quote_%s' % order_sudo.id) != now and \
            request.env.user.share and access_token:
            request.session['view_quote_%s' % order_sudo.id] = now
            body = _('Quotation viewed by supplier %s') % order_sudo.partner_id.name
            _message_post_helper(
                'purchase.order', order_sudo.id, body,
                token=order_sudo.access_token, message_type='notification')

        values = {
            'purchase_order': order_sudo,
            'message': message,
            'token': access_token,
            'bootstrap_formatting': True,
            'partner_id': order_sudo.partner_id.id,
            'report_type': 'html',
            'action': order_sudo._get_portal_return_action(),
        }
        if order_sudo.company_id:
            values['res_company'] = order_sudo.company_id

        if order_sudo.state in ('draft', 'sent', 'cancel'):
            history = request.session.get('my_quotations_history', [])
        else:
            history = request.session.get('my_orders_history', [])
        values.update(get_records_pager(history, order_sudo))

        return request.render(
            'purchase_rfq_online.purchase_order_portal_template', values)

    @http.route(['/my/purchase/<int:order_id>/accept'], type='json', auth="public",
                website=True)
    def purchase_order_rfq_accept(
            self, order_id, access_token=None, name=None, signature=None):
        # get from query string if not on json param
        access_token = access_token or request.httprequest.args.get('access_token')
        try:
            order_sudo = self._document_check_access(
                'purchase.order', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return {'error': _('Invalid order.')}

        if not signature:
            return {'error': _('Signature is missing.')}

        if order_sudo.state not in ('draft', 'sent'):
            query_string = '&message=cant_sign'
            return {
                'force_refresh': True,
                'redirect_url': order_sudo.get_portal_url(query_string=query_string),
            }

        try:
            order_sudo.write({
                'signed_by': name,
                'signed_on': fields.Datetime.now(),
                'signature': signature,
            })
        except (TypeError, binascii.Error) as e:
            return {'error': _('Invalid signature data.')}

        report_xml_id = 'purchase.report_purchase_quotation'
        if order_sudo.state not in ('draft', 'sent', 'cancel'):
            report_xml_id = 'purchase.action_report_purchase_order'
        #pdf = request.env.ref(
        #    report_xml_id).sudo().render_qweb_pdf([order_sudo.id])[0]

        #_message_post_helper(
        #    'purchase.order', order_sudo.id, _('Quotation is sent by %s') % (name,),
        #    attachments=[('%s.pdf' % order_sudo.name, pdf)],
        #    **({'token': access_token} if access_token else {}))

        query_string = '&message=sign_ok'
        return {
            'force_refresh': True,
            'redirect_url': order_sudo.get_portal_url(query_string=query_string),
        }

    @http.route(['/my/purchase/<int:order_id>/decline'], type='http', auth="public",
                methods=['POST'], website=True)
    def purchase_order_rfq_decline(self, order_id, access_token=None, **post):
        try:
            order_sudo = self._document_check_access(
                'purchase.order', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        message = post.get('decline_message')

        query_string = False
        if message:
            order_sudo.button_cancel()
            _message_post_helper(
                'purchase.order', order_id, message,
                **{'token': access_token} if access_token else {})
        else:
            query_string = "&message=cant_reject"

        return request.redirect(
            order_sudo.get_portal_url(query_string=query_string))


