# -*- coding: utf-8 -*-

from odoo import api, fields, models
from datetime import date

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    #Redondeo de decimales a 2 digitos en el precio de venta y costo en el producto 

    #PRECIO DE VENTA
    @api.onchange('list_price')
    def set_price(self):
        for record in self:
            record.list_price = round(record.list_price,2)

    #PRECIO DE COSTO(Funcion existente)
    @api.depends_context('company')
    @api.depends('product_variant_ids', 'product_variant_ids.standard_price')
    def _compute_standard_price(self):
        # Depends on force_company context because standard_price is company_dependent
        # on the product_product
        unique_variants = self.filtered(lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            template.standard_price = round(template.product_variant_ids.standard_price,2)
        for template in (self - unique_variants):
            template.standard_price = 0.0