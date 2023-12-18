from odoo import api, fields, models

class product_rule(models.Model):
    _name = "product.rule"
    _description = "Product Rule"  
    
    name = fields.Char(string="Name")
    active = fields.Boolean(string="Active")
    factor = fields.Selection(
        [('sale_base', 'Sale Base'), ('rating_base', 'Rating Base')], string="Rule Type",
        required=True)
    threshold = fields.Float(string="Threshold Value")

    threshold_amount = fields.Integer(string="Threshold Amount")