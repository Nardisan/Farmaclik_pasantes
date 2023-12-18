from odoo import models, fields, api, tools, _
from datetime import timedelta, datetime, timezone, date


class PosConfig(models.Model):
    _inherit = 'pos.config'

    @api.model
    def _default_discount(self):
        product = self.env['product.product'].search([('default_code', '=', 'DISC')], limit=1)
        return product
    
    product_discount = fields.Many2one('product.product', string='Discount Product',
     help='The product used to model the discount for commision of doctor.', default=_default_discount)
    
