import logging

from odoo import http
from odoo.exceptions import AccessError, MissingError, UserError
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from werkzeug.utils import redirect
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.addons.website_sale_delivery.controllers.main import WebsiteSaleDelivery

_logger = logging.getLogger(__name__)


class UserMemberSystem(http.Controller):

    @http.route(['/shop-membership'], type='http', auth="public", website=True)
    def membership_product(self, **kw):
        values = {}
        products = http.request.env['product.template']
        product_ids = products.search([('is_membership', '=', True), ('website_published', '=', True)])
        product_ids = product_ids.sorted(key=lambda product_id: product_id.user_membership_plan_id.sequence)
        values.update(product_ids=product_ids, page_name='Membership', )
        return http.request.render("user_membership.membership_products", values)

    @http.route(['/shop/membership/<int:product_variant_id>'], type='http', auth="public", website=True)
    def shop_membership_product(self, product_variant_id, **kw):
        products = http.request.env['product.product']
        product_id = products.search([('id', '=', product_variant_id)])
        order = request.website.sale_get_order(force_create=1)
        order.order_line = False
        request.session.update(sale_last_order_id=order.id)
        values = {
            'product_id': product_id.id,
            'product_uom_qty': 1,
            'order_id': order.id,
            'product_uom': 1,
            'price_unit': product_id.lst_price,
            'tax_id': product_id.taxes_id.ids
        }
        http.request.env['sale.order.line'].sudo().create(values)
        return redirect('/shop/payment')


class WebsiteSaleDel(WebsiteSaleDelivery):
    def _get_shop_payment_values(self, order, **kwargs):
        values = super(WebsiteSaleDel, self)._get_shop_payment_values(order, **kwargs)
        if 'deliveries' in values.keys():
            delivery_carriers = order._get_delivery_methods_as_membership()
            values['deliveries'] = delivery_carriers.sudo()
        return values


class InheritWebsiteSale(WebsiteSale):
    @http.route()
    def pricelist_change(self, pl_id, **post):
        values = super(InheritWebsiteSale, self).pricelist_change(pl_id=pl_id, post=post)
        partner = request.env.user.sudo().partner_id

        if partner.is_membership_active and not partner.is_membership_suspend:
            membership_pricelist = partner \
                .user_membership_id \
                .user_membership_plan_id \
                .pricelist_id.id

            request.session['website_sale_current_pl'] = membership_pricelist
            request.website.sale_get_order(force_pricelist=membership_pricelist)

        return values

    @http.route()
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        res = super().shop(page, category, search, ppg, **post)

        pl = request.website.sale_get_order().pricelist_id

        self.pricelist_change(pl)

        return res

    @http.route("/cart/check-membership-product", type="json", auth="public", website=True)
    def _get_product_in_cart(self):
        order = request.website.sale_get_order()

        return any(order.order_line.mapped("product_id.is_membership"))

    def _get_products_recently_viewed(self):
        res = super(InheritWebsiteSale, self)._get_products_recently_viewed()
        products_list_new = []
        user = http.request.env.user
        user_membership_id = user.user_membership_id
        if res:
            for item in res.get('products'):
                products = http.request.env['product.template'].sudo()
                product_id = products.search([('id', '=', item['product_template_id'])])

                if not product_id.not_show_in_website:
                    products_list_new.append(item)
                if product_id.not_show_in_website and user_membership_id and user_membership_id.user_membership_plan_id.id in product_id.user_membership_plan_ids.ids:
                    products_list_new.append(item)

        res.update(products=products_list_new)
        return res

    @http.route(['/shop/payment'], type='http', auth="public", website=True, sitemap=False)
    def payment(self, **post):
        res = super(InheritWebsiteSale, self).payment(**post)
        order = request.website.sale_get_order()

        membership_exclusive_items_lines = order.order_line.filtered(
            lambda line: line.product_id.not_show_in_website and line.product_id.user_membership_plan_ids)
        if membership_exclusive_items_lines:
            partner_has_membership = order.partner_id.user_membership_id and order.partner_id.is_membership_active
            if partner_has_membership:
                partner_membership_id = order.partner_id.user_membership_id
                for item_line in membership_exclusive_items_lines:
                    if partner_membership_id.id not in item_line.product_id.user_membership_plan_ids.ids:
                        res.qcontext["errors"].append(("Exclusive Product Error", item_line.product_id.display_name +
                                                       " only for customers with " + ", ".join(
                            item_line.product_id.user_membership_plan_ids.mapped('name')) + " Remove from cart."))
                        res.qcontext.pop('acquirers', '')
                        res.qcontext.pop('tokens', '')
                        res.qcontext.pop('deliveries', '')
                        res.qcontext.pop('delivery_has_storable', '')
                        res.qcontext.pop('delivery_action_id', '')
                        break
            else:
                res.qcontext["errors"].append(("Exclusive Product Error", ", ".join(
                    membership_exclusive_items_lines.product_id.mapped(
                        'display_name')) + " only for customers with Membership! Remove from cart."))
                res.qcontext.pop('acquirers', '')
                res.qcontext.pop('tokens', '')
                res.qcontext.pop('deliveries', '')
                res.qcontext.pop('delivery_has_storable', '')
                res.qcontext.pop('delivery_action_id', '')

        validation_res = order.validate_membership_order()
        if validation_res and validation_res.get("error"):
            if res.qcontext.get("errors"):
                res.qcontext["errors"].append(("Membership Validation Error", validation_res.get("error")))
            else:
                res.qcontext.update({"errors": [("Membership Validation Error", validation_res.get("error"))]})
                res.qcontext.pop('acquirers', '')
                res.qcontext.pop('tokens', '')
                res.qcontext.pop('deliveries', '')
                res.qcontext.pop('delivery_has_storable', '')
                res.qcontext.pop('delivery_action_id', '')
        return res


class MembershipCustomerPortal(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id

        UserMembership = request.env['user.membership']
        if 'membership_count' in counters:
            values['membership_count'] = UserMembership.search_count(
                [('partner_id', '=', partner.id)])
        return values

    @http.route(['/my/membership', '/my/membership/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_membership(self, page=1, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        UserMembership = request.env['user.membership']

        domain = [
            ('partner_id', '=', partner.id)
        ]
        membership_counts = UserMembership.search_count(domain)
        pager = portal_pager(
            url="/my/membership",
            url_args={},
            total=membership_counts,
            page=page,
            step=self._items_per_page
        )
        user_membership_ids = UserMembership.search(
            domain,
            order='id desc',
            limit=self._items_per_page, offset=pager['offset'])
        values.update({
            'user_membership_ids': user_membership_ids.sudo(),
            'page_name': 'User Membership',
            'pager': pager,
            'default_url': '/my/membership',
        })
        return http.request.render("user_membership.portal_my_user_membership", values)

    @http.route(['/my/membership/<int:user_membership_id>'], type='http', auth="user", website=True)
    def portal_my_user_membership_detail(self, user_membership_id, access_token=None, report_type=None, download=False,
                                         **kw):
        try:
            membership_sudo = self._document_check_access('user.membership', user_membership_id,
                                                          access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        values = {}
        user_membership_id = membership_sudo.search([('id', '=', user_membership_id)])
        values.update(user_membership_id=user_membership_id, page_name='User Membership',
                      company_id=http.request.env.company, )

        return http.request.render("user_membership.portal_page", values)

    @http.route(['/cancel-membership/<int:user_membership_id>'], type='http', auth="user", website=True)
    def cancel_membership(self, user_membership_id, access_token=None, **kw):
        try:
            membership_sudo = self._document_check_access('user.membership', user_membership_id,
                                                          access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        membership_id = membership_sudo.search([('id', '=', user_membership_id)])
        membership_id.mem_cancel()
        if kw.get("reason"):
            membership_id.cancel_reason = kw.get("reason")
        return request.redirect('/my/membership/%s' % membership_id.id)
