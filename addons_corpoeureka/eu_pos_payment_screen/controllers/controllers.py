# -*- coding: utf-8 -*-
# from odoo import http


# class EuPosPaymentScreen(http.Controller):
#     @http.route('/eu_pos_payment_screen/eu_pos_payment_screen/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/eu_pos_payment_screen/eu_pos_payment_screen/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('eu_pos_payment_screen.listing', {
#             'root': '/eu_pos_payment_screen/eu_pos_payment_screen',
#             'objects': http.request.env['eu_pos_payment_screen.eu_pos_payment_screen'].search([]),
#         })

#     @http.route('/eu_pos_payment_screen/eu_pos_payment_screen/objects/<model("eu_pos_payment_screen.eu_pos_payment_screen"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('eu_pos_payment_screen.object', {
#             'object': obj
#         })
