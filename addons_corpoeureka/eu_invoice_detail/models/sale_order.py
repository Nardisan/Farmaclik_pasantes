# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning, UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    invoice_rel_status  = fields.Selection(related="invoice_ids.state",string="Estado Factura Relacionada")
    invoice_rel_pay     = fields.Selection(related="invoice_ids.payment_state",string="Pago Factura Relacionada")
    invoice_rel         = fields.Char(related="invoice_ids.name",string="Factura Relacionada")
    invoice_ref         = fields.Char(related="invoice_ids.ref",string="Ref Factura Relacionada")
