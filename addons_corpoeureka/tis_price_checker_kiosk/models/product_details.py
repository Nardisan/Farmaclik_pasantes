# -*- coding: utf-8 -*-
# This module and its content is copyright of Technaureus Info Solutions Pvt. Ltd.
# - © Technaureus Info Solutions Pvt. Ltd 2020. All rights reserved.

from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    
    @api.model
    def get_details(self, barcode):
        check_barcode = barcode
        product_details = self.search([('barcode', '=', check_barcode)])
        return product_details.id, product_details.name, product_details.list_price, product_details.barcode, \
               product_details.taxes_id.amount, self.env['res.currency'].search([('name', '=', 'VEF')], limit=1).rate, product_details.currency_id.symbol, product_details.uom_id.name, \
		product_details.default_code, product_details.with_context({ 'location': 8 }).qty_available

