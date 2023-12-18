# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError

class ProductProduct(models.Model):
    _inherit = 'product.product'

    default_code = fields.Char(copy=False)

    @api.constrains('default_code')
    def _check_unique_default_code(self):
        for product in self:
            count = self.search_count([('default_code', '=', product.default_code), ('id', '!=', product.id)])
            if count > 0:
                raise ValidationError('La referencia interna del producto deber ser unica')