# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductPriceHistory(models.Model):
    """
    Modelo para registrar los cambios de precios de los productos.
    """

    _name = 'add_product_price_history.product_price_history'
    _description = ('Historial con los cambios de precios de los productos. Se registra el precio al modificar y '
                    'crear productos, y al inicializar el módulo.')

    product = fields.Many2one('product.template', string="Producto", required=True)
    price = fields.Float(string="Precio", required=True)
    type = fields.Selection(
        [('actualizacion', 'Actualización'), ('creacion', 'Creación'), ('inicializacion', 'Inicialización')],
        string="Tipo",
        required=True)
    user = fields.Many2one('res.users', string="Usuario", default=lambda self: self.env.user.id)

    def __str__(self):
        return f"{self.product.name} - {self.description}"


class ProductWithHistory(models.Model):
    """
    Modelo para extender el producto y agregar el campo de historial de precios, ademas de sobre escribir el metodo de
    escritura para registrar los cambios de precios. Tambien se define el metodo para inicializar los precios de los
    productos por medio del cron.
    """

    _inherit = 'product.template'

    price_history = fields.One2many('add_product_price_history.product_price_history', 'product',
                                    string="Historial de precios")

    @api.model
    def register_starting_price(self):
        """
        Metodo para registrar los precios iniciales de los productos al inicializar el modulo, usando el cron.
        """

        products = self.env['product.template'].search([])

        for product in products:
            price_history = self.env['add_product_price_history.product_price_history'].create({
                'product': product.id,
                'price': product.standard_price,
                'type': 'inicializacion',
                'user': self.env.user.id
            })
        return True

    def write(self, vals):
        """
        Sobre escritura del metodo write para registrar los cambios de precios de los productos.
        Se compara el precio anterior con el nuevo para determinar si es un cambio y se registra como una actualizacion
        o creacion si no hay registros para ese producto.
        """
        old_price = self.standard_price

        result: bool = super(ProductWithHistory, self).write(vals)

        is_creation = len((self.env['add_product_price_history.product_price_history']
                           .search([('product', '=', self.id)]))) == 0

        record_type = 'creacion' if is_creation else 'actualizacion'

        if 'standard_price' in vals and old_price != vals['standard_price']:
            product = self.id
            price = vals['standard_price']  # help me here

            price_history = self.env['add_product_price_history.product_price_history'].create({
                'product': product,
                'price': price,
                'type': record_type,
                'user': self.env.user.id
            })
        return result
