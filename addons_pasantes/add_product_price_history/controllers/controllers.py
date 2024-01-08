# -*- coding: utf-8 -*-
# from odoo import http


# class AddProductPriceHistory(http.Controller):
#     @http.route('/add_product_price_history/add_product_price_history/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/add_product_price_history/add_product_price_history/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('add_product_price_history.listing', {
#             'root': '/add_product_price_history/add_product_price_history',
#             'objects': http.request.env['add_product_price_history.add_product_price_history'].search([]),
#         })

#     @http.route('/add_product_price_history/add_product_price_history/objects/<model("add_product_price_history.add_product_price_history"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('add_product_price_history.object', {
#             'object': obj
#         })
