# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class PosOrder(models.Model):
    _inherit = 'pos.order'



    show_currency = fields.Many2one('res.currency', string='Moneda Ref',related="session_id.config_id.show_currency",store=True)
    @api.depends('amount_tax','amount_total','amount_paid','session_id','date_order')
    def _compute_montos_ref(self):
        for rec in self:
            rec.amount_tax_ref = rec.currency_id._convert(rec.amount_tax, rec.session_id.config_id.show_currency, rec.company_id, rec.date_order or fields.Date.today())
            rec.amount_total_ref = rec.currency_id._convert(rec.amount_total, rec.session_id.config_id.show_currency, rec.company_id, rec.date_order or fields.Date.today())
            rec.amount_paid_ref = rec.currency_id._convert(rec.amount_paid, rec.session_id.config_id.show_currency, rec.company_id, rec.date_order or fields.Date.today())

    amount_tax_ref = fields.Float(string='Impuestos Ref', readonly=True,compute="_compute_montos_ref")
    amount_total_ref = fields.Float(string='Total Ref',  readonly=True,compute="_compute_montos_ref")
    amount_paid_ref = fields.Float(string='Total Pagado (con redondeo) Ref',readonly=True,compute="_compute_montos_ref")


