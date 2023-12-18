from odoo import api, fields, models, _

class ir_filters(models.Model):
    _inherit = "ir.filters"
    
    filter_ids=fields.One2many('slider.filter','filter_id','Filter ids')
