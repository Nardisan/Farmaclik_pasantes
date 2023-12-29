# -*- coding: utf-8 -*-
# from odoo import http


# class AddInvoiceNumber(http.Controller):
#     @http.route('/add_invoice_number/add_invoice_number/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/add_invoice_number/add_invoice_number/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('add_invoice_number.listing', {
#             'root': '/add_invoice_number/add_invoice_number',
#             'objects': http.request.env['add_invoice_number.add_invoice_number'].search([]),
#         })

#     @http.route('/add_invoice_number/add_invoice_number/objects/<model("add_invoice_number.add_invoice_number"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('add_invoice_number.object', {
#             'object': obj
#         })
