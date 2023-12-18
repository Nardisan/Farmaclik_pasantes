
from odoo import models, fields, api, _
from odoo.exceptions import Warning, UserError

class StockPicking(models.Model):
    _inherit = 'stock.picking'

  
    invoice_rel             = fields.Char(related="sale_id.invoice_ids.name",string="Factura Relacionada")
    sale_rel                = fields.Char(related="sale_id.name",string="SO Relacionada")
    invoice_rel_status      = fields.Selection(related="sale_id.invoice_ids.state",string="Estado Factura Relacionada")
    invoice_rel_pay         = fields.Selection(related="sale_id.invoice_ids.payment_state",string="Pago Factura Relacionada")
    sale_rel_status         = fields.Selection(related="sale_id.state",string="Estado SO Relacionada")
    
    invoice_rel_po             = fields.Char(related="purchase_id.invoice_ids.name",string="Factura Relacionada")
    purchase_rel                = fields.Char(related="purchase_id.name",string="PO Relacionada")
    invoice_rel_status_po      = fields.Selection(related="purchase_id.invoice_ids.state",string="Estado Factura Relacionada")
    invoice_rel_pay_po         = fields.Selection(related="purchase_id.invoice_ids.payment_state",string="Pago Factura Relacionada")
    purchase_rel_status         = fields.Selection(related="purchase_id.state",string="Estado PO Relacionada")