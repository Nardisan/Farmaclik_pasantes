from odoo import api, fields, models
    
class product_pricelist_item(models.Model):
    _inherit = "product.pricelist.item"
    
    offer_msg = fields.Char(string="Offer Message",translate=True)
    is_display_timer = fields.Boolean(string='Display TImer')