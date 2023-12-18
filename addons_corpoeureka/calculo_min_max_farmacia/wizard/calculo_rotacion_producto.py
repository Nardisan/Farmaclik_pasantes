from odoo import models, fields, api, _
from odoo.exceptions import  ValidationError
from datetime import datetime

class CalculoRotacionProducto(models.TransientModel):

    _name = "calculo.rotacion.producto"
    _description = "Establecer la rotación del productos (Alta, Media, Baja) segun valores del máximo"

    # solo_estos_product = fields.Many2one('lista.productos.min.max', string='Solo Estos Productos')
    # excluyendo_estos_product = fields.Many2one('lista.productos.min.max', string='Excluyendo Estos Productos')

    # solo_estos_product_ids = fields.Many2many('product.product', 'product_solo', 'product_id', 'solo_id', string='Solo Estos Productos', domain="[('type', '=', 'product')]",  help='Para todos los productos dejar esta lista vacia', default=[])
    # excluyendo_estos_product_ids = fields.Many2many('product.product', 'product_excluyendo', 'product_id', 'excluyendo_id',  string='Excluyendo Estos Productos', domain="[('type', '=', 'product')]", default=[])
    
    # elementos_por_lote = fields.Integer(string='Elementos por Lote', required=True, default = 2000 )
    # lotes_total = fields.Integer(string='Lotes Total',  compute="calculo_lotes_total" )
    # lote = fields.Integer(string='Lote', required=True)
   
    # @api.depends('lote')
    # def calculo_lotes_total(self):

    #     productos = self.env['product.template'].search([('type', '=', 'product')])
    #     self.lotes_total = self.ceil(len(productos) / self.elementos_por_lote)


    # def ceil(self, x):
    #     return int(x) + int((x>0) and (x - int(x)) > 0)

    def calcular_rotacion_producto(self):

        productos = self.env['product.template'].search([('type', '=', 'product')], order="max_stock_fgg desc")
        indice = 0

        for producto in productos:

            if indice < 300 :
                producto.write({ "rotacion_fgg": 'Alta' })

            if indice > 300 and indice < 800 :
                 producto.write({ "rotacion_fgg": 'Media' })

            if indice > 800 :
                 producto.write({ "rotacion_fgg": 'Baja' })

            indice = indice + 1

        productos = self.env['product.template'].search([('type', '=', 'product')], order="max_stock_pp desc")
        indice = 0

        for producto in productos:

            if indice < 300 :
                producto.write({ "rotacion_pp": 'Alta' })

            if indice > 300 and indice < 800 :
                 producto.write({ "rotacion_pp": 'Media' })

            if indice > 800 :
                 producto.write({ "rotacion_pp": 'Baja' })

            indice = indice + 1

        productos = self.env['product.template'].search([('type', '=', 'product')], order="max_stock_eg desc")
        indice = 0

        for producto in productos:

            if indice < 300 :
                producto.write({ "rotacion_eg": 'Alta' })

            if indice > 300 and indice < 800 :
                 producto.write({ "rotacion_eg": 'Media' })

            if indice > 800 :
                 producto.write({ "rotacion_eg": 'Baja' })

            indice = indice + 1

        productos = self.env['product.template'].search([('type', '=', 'product')], order="max_stock_gu desc")
        indice = 0

        for producto in productos:

            if indice < 300 :
                producto.write({ "rotacion_gu": 'Alta' })

            if indice > 300 and indice < 800 :
                 producto.write({ "rotacion_gu": 'Media' })

            if indice > 800 :
                 producto.write({ "rotacion_gu": 'Baja' })

            indice = indice + 1

        productos = self.env['product.template'].search([('type', '=', 'product')], order="max_general_4f desc")
        indice = 0

        for producto in productos:

            if indice < 300 :
                producto.write({ "rotacion_4f": 'Alta' })

            if indice > 300 and indice < 800 :
                 producto.write({ "rotacion_4f": 'Media' })

            if indice > 800 :
                 producto.write({ "rotacion_4f": 'Baja' })

            indice = indice + 1
        
        action = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Establecer Rotación Farmacia',
                'type': 'success',
                'message': 'Rotación establecida en las farmacias',
                'sticky': True,
            }
        }

        return action




    def calcular_rotacion_producto_farmagangas(self):
 
        productos = self.env['product.template'].search([('type', '=', 'product')], order="max_stock_fgg desc")
        indice = 0

        for producto in productos:

            if indice < 300 :
                producto.with_company(50).write({ "rotacion": 'Alta' })

            if indice > 300 and indice < 800 :
                 producto.with_company(50).write({ "rotacion": 'Media' })

            if indice > 800 :
                 producto.with_company(50).write({ "rotacion": 'Baja' })

            indice = indice + 1

        action = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Establecer Rotación Farmacia',
                'type': 'success',
                'message': 'Rotación establecida en Farmagangas',
                'sticky': True,
            }
        }

        return action

    def calcular_rotacion_producto_paseo_paraparal(self):

        productos = self.env['product.template'].search([('type', '=', 'product')], order="max_stock_pp desc")
        indice = 0
        
        for producto in productos:

            if indice < 300 :
                producto.with_company(1).write({ "rotacion": 'Alta' })

            if indice > 300 and indice < 800 :
                 producto.with_company(1).write({ "rotacion": 'Media' })

            if indice > 800 :
                 producto.with_company(1).write({ "rotacion": 'Baja' })

            indice = indice + 1
       
        action = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Establecer Rotación Farmacia',
                'type': 'success',
                'message': 'Rotación establecida en Paseo Paraparal',
                'sticky': True,
            }
        }

        return action
        
    