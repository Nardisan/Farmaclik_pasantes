# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, timedelta

class PosOrderNegative(models.Model):
    _name = 'pos.order.negative'
    _description = 'Report de producto en negativo'

    product = fields.Char(string="Producto")
    qty =fields.Integer(string="Cantidad Vendida")
    date = fields.Datetime(string="Fecha")
    employee = fields.Char(string="Cajero")
    order = fields.Char(string="Pedido")

    def _stock_negativo(self):

        day_t = datetime.now()
        t_date = day_t.replace(hour=0, minute=0, second=0)
        day = datetime.now() - timedelta(days=1)
        inic_date = day.replace(hour=0, minute=0, second=0)

        orders = self.env['pos.order'].search([('date_order', '>=', inic_date),('date_order', '<', t_date)])
        print(len(orders))

        lines=[]
        product=[]
        
        for order in orders:
            for line in order.lines:
                lines.append(line) # lista de pedidos 
                if line.product_id.id not in product:
                    product.append(line.product_id.id)#lista de producto
        
        products = self.env['product.product'].search([('id', 'in', product),('qty_available', '<', 0)])

        list_new = []

        for product in products:
            qty=0
            for line in lines:
                if qty < abs(product.qty_available):
                    if product.id == line.product_id.id:
                        #escrbir en la lista nueva
                        # list_new.append
                        self.create({
                            'product': product.name,
                            'qty': line.qty,
                            'date': line.order_id.date_order,
                            'employee': line.order_id.employee_id.name,
                            'order': line.order_id.name
                        })
                        qty += line.qty