# -*- coding: utf-8 -*-
# from odoo import http


# class MenuReport(http.Controller):
#     @http.route('/menu_report/menu_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/menu_report/menu_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('menu_report.listing', {
#             'root': '/menu_report/menu_report',
#             'objects': http.request.env['menu_report.menu_report'].search([]),
#         })

#     @http.route('/menu_report/menu_report/objects/<model("menu_report.menu_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('menu_report.object', {
#             'object': obj
#         })
