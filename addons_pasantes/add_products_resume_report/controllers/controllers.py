# -*- coding: utf-8 -*-
# from odoo import http


# class AddProductsResumeReport(http.Controller):
#     @http.route('/add_products_resume_report/add_products_resume_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/add_products_resume_report/add_products_resume_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('add_products_resume_report.listing', {
#             'root': '/add_products_resume_report/add_products_resume_report',
#             'objects': http.request.env['add_products_resume_report.add_products_resume_report'].search([]),
#         })

#     @http.route('/add_products_resume_report/add_products_resume_report/objects/<model("add_products_resume_report.add_products_resume_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('add_products_resume_report.object', {
#             'object': obj
#         })
