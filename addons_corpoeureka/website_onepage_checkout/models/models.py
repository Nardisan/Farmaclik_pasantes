# -*- coding: utf-8 -*-
##########################################################################
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
##########################################################################

from odoo import api, fields, models, _

class BillingDefaultFields(models.Model):
    _name = "billing.default.fields"

    name = fields.Char(string="Campos predeterminados para facturación", required="1")
    code = fields.Char(string="Código", required="1")

class ShippingDefaultFields(models.Model):
    _name = "shipping.default.fields"

    name = fields.Char(string="Campos predeterminados para facturación", required="1")
    code = fields.Char(string="Código", required="1")

class Website(models.Model):
    _inherit = 'website'

    @api.model
    def show_required_address_fields(self, address_type=False):
        onepage_config = self.env['onepage.checkout.config'].search([('is_active', '=', True)], limit=1)
        billing_address, shipping_address = ["name", "country_id", "email"], ["name", "country_id"]
        if onepage_config:
            if address_type == 'billing':
                for billing in onepage_config.wk_billing_required:
                    billing_address.append(billing.code)
                return billing_address

            if address_type == 'shipping':
                for shipping in onepage_config.wk_shipping_required:
                    shipping_address.append(shipping.code)
                return shipping_address
        return billing_address