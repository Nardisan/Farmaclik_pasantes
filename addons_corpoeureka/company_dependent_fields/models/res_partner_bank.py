
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ResPartnerBanck(models.Model):
    _inherit = 'res.partner.bank'

    saldo = fields.Float(string="Saldo")
    fecha_de_saldo_actualizado = fields.Date(string='Fecha de Saldo Actualizado')