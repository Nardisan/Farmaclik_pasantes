# -*- coding: utf-8 -*-

from odoo import models, fields

class PosConfig(models.Model):
    _inherit = 'pos.config'

    show_ref_input = fields.Boolean("Mostrar monto de referencia")
    edit_ref_input = fields.Boolean("Editar monto de referencia")
    fiscal_port = fields.Integer("Puerto de impresora fiscal")
    maquina= fields.Char(string="Número de registro de impresora fiscal")