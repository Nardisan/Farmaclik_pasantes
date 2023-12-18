from odoo import models,fields

class website_expertise(models.Model):
    _name = "website.expertise"
    _description = "Website Expertise"
    
    name=fields.Char("Name",required=True,translate=True)
    expertise=fields.Integer("Expertise",required=True)
    company_id=fields.Many2one('res.company', 'Company')
