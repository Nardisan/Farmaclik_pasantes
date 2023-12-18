# -*- coding: utf-8 -*-
import re
from odoo import fields, models,api
from odoo.exceptions import UserError
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.addons.website_sale.controllers.main import WebsiteSale
class Customer(CustomerPortal):
    OPTIONAL_BILLING_FIELDS = ["zipcode", "state_id", "vat","cedula", "company_name"]

class Website(models.Model):
    _inherit = 'website'

    @api.model
    def show_required_address_fields(self, address_type=False):
        onepage_config = self.env['onepage.checkout.config'].search([('is_active', '=', True)], limit=1)
        billing_address, shipping_address = ["name", "country_id", "email",'cedula'], ["name", "country_id",'street']
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

class WebsiteSale(WebsiteSale):
    def values_postprocess(self, order, mode, values, errors, error_msg):
        new_values, errors, error_msg=super().values_postprocess(order, mode, values, errors, error_msg)
        if values.get("cedula"):
            new_values['cedula']=values['cedula']
        # formate = (r"[JGPVE]{1}[-]{1}[0-9]{8}")
        # form_ci = re.compile(formate)
        # if  form_ci.match(ew_values['cedula']):
        #     errors["cedula"] = 'error de formatos'
        return new_values, errors, error_msg



    def checkout_form_validate(self, mode, all_form_values, data):
        error, error_message=super().checkout_form_validate(mode, all_form_values, data)
        formate = (r"[JGPVE]{1}[-]{1}[0-9]{8}")
        form_ci = re.compile(formate)
        if data.get('cedula') and not form_ci.match(data.get('cedula')):
            error["cedula"] = 'error de formatos'
            error_message.append(('La cedula debe cumplir con el formato V-24587874'))

        return error, error_message