# -*- coding: utf-8 -*-

from odoo import fields, models

class StockPicking(models.Model):
    _inherit = "stock.picking"

    street 		= fields.Char(related='partner_id.street',string="Dirección de Envío",store=True)
