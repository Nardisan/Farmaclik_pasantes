# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    @api.depends('price_unit','price_subtotal','price_subtotal_incl','order_id')
    def _compute_price_ref(self):
        for rec in self:
            rec.price_unit_ref = rec.currency_id._convert(rec.price_unit, rec.order_id.session_id.config_id.show_currency, rec.company_id, rec.order_id.date_order or fields.Date.today())
            rec.price_subtotal_ref = rec.currency_id._convert(rec.price_subtotal, rec.order_id.session_id.config_id.show_currency, rec.company_id, rec.order_id.date_order or fields.Date.today())
            rec.price_subtotal_incl_ref = rec.currency_id._convert(rec.price_subtotal_incl, rec.order_id.session_id.config_id.show_currency, rec.company_id, rec.order_id.date_order or fields.Date.today())

    price_unit_ref = fields.Float(string='Precio Unit Ref',compute="_compute_price_ref")
    price_subtotal_ref = fields.Float(string='Subtotal Neto Ref',compute="_compute_price_ref")
    price_subtotal_incl_ref = fields.Float(string='Subtotal Ref',compute="_compute_price_ref")