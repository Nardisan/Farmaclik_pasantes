# -*- coding: utf-8 -*-

from odoo import models, fields, api


class change_product(models.Model):
    _inherit = "product.template"
    
    
    active_ingredient_ids = fields.Many2many(string="Principio activo")
    
    profitability_id = fields.Many2one('product.profitability', string="Active Ingredient")
    
    
class ProductProfitability(models.Model):
    _name = 'product.profitability'
    _description = 'Rentabilidad del producto'

    name = fields.Float('% de rentabilidad')
    description = fields.Char('Descripcion')