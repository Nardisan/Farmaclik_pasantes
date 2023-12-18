# -*- coding: utf-8 -*-

from odoo import fields, models

class AccountMove(models.Model):
    _inherit = "account.move"

    ciudad 		= fields.Many2one(related='partner_id.ciudad',string="Ciudades",store=True)
    sector 		= fields.Many2one(related='partner_id.sector',string="Sector",store=True)
    street 		= fields.Char(related='partner_shipping_id.street',string="Dirección de Envío",store=True)
