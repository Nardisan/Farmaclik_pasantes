# -*- coding: utf-8 -*-
# from odoo import http


# class UserActionsNotifier(http.Controller):
#     @http.route('/user_actions_notifier/user_actions_notifier/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/user_actions_notifier/user_actions_notifier/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('user_actions_notifier.listing', {
#             'root': '/user_actions_notifier/user_actions_notifier',
#             'objects': http.request.env['user_actions_notifier.user_actions_notifier'].search([]),
#         })

#     @http.route('/user_actions_notifier/user_actions_notifier/objects/<model("user_actions_notifier.user_actions_notifier"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('user_actions_notifier.object', {
#             'object': obj
#         })
