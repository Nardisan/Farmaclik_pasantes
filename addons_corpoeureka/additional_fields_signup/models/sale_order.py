# -*- coding: utf-8 -*-

from odoo import fields, models

class SaleOrder(models.Model):
    _inherit = "sale.order"

    ciudad 		= fields.Many2one(related='partner_id.ciudad',string="Ciudades",store=True)
    sector 		= fields.Many2one(related='partner_id.sector',string="Sector",store=True)
    street 		= fields.Char(related='partner_shipping_id.street',string="Dirección de Envío",store=True)
