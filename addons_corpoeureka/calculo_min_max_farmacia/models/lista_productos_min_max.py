from odoo.exceptions import Warning
from odoo import models, fields, api, _

class ListaProductosMinMax(models.Model):

    _name = "lista.productos.min.max"
    _description = "Lista de productos para los mínimos y máximos excluyente o exclusiva"

    name = fields.Char(string="Nombre", required=True)
    lista_productos = fields.Many2many('product.product', string='Lista de Productos', domain="[('type', '=', 'product')]", default=[])