# -*- coding: utf-8 -*-

from odoo import http

class PosController(http.Controller):
    @http.route('/pos/fiscal/print', type='http', auth="public")
    def print_default(self):
        return 1

    @http.route(['/fiscal/print_x', '/fiscal/print_z'], type='json', auth="public", methods=["POST"])
    def print_specials(self):
        return 1