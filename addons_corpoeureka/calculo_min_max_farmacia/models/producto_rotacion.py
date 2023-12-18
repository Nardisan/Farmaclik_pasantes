from odoo import fields, models, api, _
from datetime import datetime, date, timedelta

class ProductoRotacion(models.Model):

    _inherit = "product.template"

    rotacion_fgg = fields.Selection([('Baja', 'Baja'), ('Media', 'Media'), ('Alta', 'Alta')], string='Rotación FGG' )
    rotacion_pp = fields.Selection([('Baja', 'Baja'), ('Media', 'Media'), ('Alta', 'Alta')], string='Rotación PP' )
    rotacion_eg = fields.Selection([('Baja', 'Baja'), ('Media', 'Media'), ('Alta', 'Alta')], string='Rotación EG' )
    rotacion_gu = fields.Selection([('Baja', 'Baja'), ('Media', 'Media'), ('Alta', 'Alta')], string='Rotación GU' )
    rotacion_4f = fields.Selection([('Baja', 'Baja'), ('Media', 'Media'), ('Alta', 'Alta')], string='Rotación 4F' )

